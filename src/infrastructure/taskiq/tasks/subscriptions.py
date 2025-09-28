from typing import Optional

from dishka import FromDishka
from dishka.integrations.taskiq import inject
from loguru import logger

from src.core.enums import PurchaseType
from src.infrastructure.database.models.dto import PlanSnapshotDto, SubscriptionDto, UserDto
from src.infrastructure.taskiq.broker import broker
from src.services.remnawave import RemnawaveService
from src.services.subscription import SubscriptionService

from .redirects import redirect_to_failed_payment_task, redirect_to_successed_payment_task


@broker.task
@inject
async def purchase_subscription_task(
    user: UserDto,
    plan: PlanSnapshotDto,
    purchase_type: PurchaseType,
    subscription: Optional[SubscriptionDto],
    remnawave_service: FromDishka[RemnawaveService],
    subscription_service: FromDishka[SubscriptionService],
) -> None:
    logger.info(f"Processing {purchase_type=} for user {user.telegram_id}")

    try:
        if purchase_type == PurchaseType.NEW:
            created_user = await remnawave_service.create_user(user, plan)
            new_subscription = SubscriptionDto(
                user_remna_id=created_user.uuid,
                status=created_user.status,
                expire_at=created_user.expire_at,
                url=created_user.short_uuid,
                plan=plan,
            )
            await subscription_service.create(user, new_subscription)
            logger.debug(f"Created new subscription for user {user.telegram_id}")

        elif purchase_type == PurchaseType.RENEW:
            if not subscription:
                logger.error(f"No subscription found for renewal for user {user.telegram_id}")
                await redirect_to_failed_payment_task.kiq(user, purchase_type)
                return

            updated_user = await remnawave_service.updated_user(
                user=user,
                plan=plan,
                uuid=subscription.user_remna_id,
            )
            subscription.expire_at = updated_user.expire_at
            subscription.plan = plan
            await subscription_service.update(subscription)
            logger.debug(f"Renewed subscription for user {user.telegram_id}")

        elif purchase_type == PurchaseType.CHANGE:
            if not subscription:
                logger.error(f"No subscription found for change for user {user.telegram_id}")
                await redirect_to_failed_payment_task.kiq(user, purchase_type)
                return

            updated_user = await remnawave_service.updated_user(
                user=user,
                plan=plan,
                uuid=subscription.user_remna_id,
            )
            new_subscription = SubscriptionDto(
                user_remna_id=updated_user.uuid,
                status=updated_user.status,
                expire_at=updated_user.expire_at,
                url=updated_user.short_uuid,
                plan=plan,
            )
            await subscription_service.create(user, new_subscription)
            logger.debug(f"Changed subscription for user {user.telegram_id}")

        else:
            logger.error(f"Unknown purchase type: {purchase_type}")
            await redirect_to_failed_payment_task.kiq(user, purchase_type)
            return

        await redirect_to_successed_payment_task.kiq(user, purchase_type)

    except Exception as exception:
        logger.exception(
            f"Failed to process {purchase_type=} for user {user.telegram_id}: {exception}"
        )
        await redirect_to_failed_payment_task.kiq(user, purchase_type)
