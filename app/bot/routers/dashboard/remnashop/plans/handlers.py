from decimal import Decimal, InvalidOperation

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, SubManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from loguru import logger

from app.bot.states import RemnashopPlans
from app.core.constants import APP_CONTAINER_KEY, USER_KEY
from app.core.container import AppContainer
from app.core.enums import Currency, PlanAvailability, PlanType
from app.core.utils.adapter import DialogDataAdapter
from app.core.utils.formatters import format_log_user
from app.db.models.dto import PlanDto, PlanDurationDto, PlanPriceDto, UserDto


async def on_name_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    dialog_manager.show_mode = ShowMode.EDIT
    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    logger.debug(f"{format_log_user(user)} Attempted to set plan name")

    if message.text is None:
        logger.warning(f"{format_log_user(user)} Provided empty plan name input")
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-plan-wrong-name",
        )
        return

    if await container.services.plan.get_by_name(name=message.text):
        logger.warning(
            f"{format_log_user(user)} Tried to set plan name to "
            f"'{message.text}', which already exists"
        )
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-plan-wrong-name",
        )
        return

    adapter = DialogDataAdapter(dialog_manager)
    plan = adapter.load(PlanDto)

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for name input")
        return

    plan.name = message.text
    adapter.save(plan)

    logger.info(f"{format_log_user(user)} Successfully set plan name to '{plan.name}'")
    await dialog_manager.switch_to(state=RemnashopPlans.PLAN)


async def on_type_selected(
    callback: CallbackQuery,
    widget: Select[PlanType],
    dialog_manager: DialogManager,
    selected_type: PlanType,
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    adapter = DialogDataAdapter(dialog_manager)
    plan = adapter.load(PlanDto)

    logger.debug(f"{format_log_user(user)} Selected plan type '{selected_type}'")

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for type selection")
        return

    plan.type = selected_type
    adapter.save(plan)

    logger.info(f"{format_log_user(user)} Successfully updated plan type to '{plan.type.name}'")
    await dialog_manager.switch_to(state=RemnashopPlans.PLAN)


async def on_availability_selected(
    callback: CallbackQuery,
    widget: Select[PlanAvailability],
    dialog_manager: DialogManager,
    selected_availability: PlanAvailability,
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    adapter = DialogDataAdapter(dialog_manager)
    plan = adapter.load(PlanDto)

    logger.debug(f"{format_log_user(user)} Selected plan availability '{selected_availability}'")

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for availability selection")
        return

    plan.availability = selected_availability
    adapter.save(plan)

    logger.info(
        f"{format_log_user(user)} Successfully updated plan availability to '{plan.availability}'"
    )
    await dialog_manager.switch_to(state=RemnashopPlans.PLAN)


async def on_active_toggle(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    adapter = DialogDataAdapter(dialog_manager)
    plan = adapter.load(PlanDto)

    logger.debug(f"{format_log_user(user)} Attempted to toggle plan active status")

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for active toggle")
        return

    plan.is_active = not plan.is_active
    adapter.save(plan)
    logger.info(
        f"{format_log_user(user)} Successfully toggled plan active status to '{plan.is_active}'"
    )


async def on_traffic_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    dialog_manager.show_mode = ShowMode.EDIT
    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    logger.debug(f"{format_log_user(user)} Attempted to set plan traffic limit")

    if message.text is None or not (message.text.isdigit() and int(message.text) > 0):
        logger.warning(
            f"{format_log_user(user)} Provided invalid traffic limit input: '{message.text}'"
        )
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-plan-wrong-number",
        )
        return

    number = int(message.text)
    adapter = DialogDataAdapter(dialog_manager)
    plan = adapter.load(PlanDto)

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for traffic input")
        return

    plan.traffic_limit = number
    adapter.save(plan)

    logger.info(
        f"{format_log_user(user)} Successfully set plan traffic limit to '{plan.traffic_limit}'"
    )
    await dialog_manager.switch_to(state=RemnashopPlans.PLAN)


async def on_devices_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    dialog_manager.show_mode = ShowMode.EDIT
    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    logger.debug(f"{format_log_user(user)} Attempted to set plan device limit")

    if message.text is None or not (message.text.isdigit() and int(message.text) > 0):
        logger.warning(
            f"{format_log_user(user)} Provided invalid device limit input: '{message.text}'"
        )
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-plan-wrong-number",
        )
        return

    number = int(message.text)
    adapter = DialogDataAdapter(dialog_manager)
    plan = adapter.load(PlanDto)

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for devices input")
        return

    plan.device_limit = number
    adapter.save(plan)

    logger.info(
        f"{format_log_user(user)} Successfully set plan device limit to '{plan.device_limit}'"
    )
    await dialog_manager.switch_to(state=RemnashopPlans.PLAN)


async def on_duration_selected(
    callback: CallbackQuery,
    widget: Button,
    sub_manager: SubManager,
) -> None:
    user: UserDto = sub_manager.middleware_data[USER_KEY]
    sub_manager.dialog_data["duration_selected"] = int(sub_manager.item_id)
    logger.debug(f"{format_log_user(user)} Selected duration '{sub_manager.item_id}' days")
    await sub_manager.switch_to(state=RemnashopPlans.PRICES)


async def on_duration_removed(
    callback: CallbackQuery,
    widget: Button,
    sub_manager: SubManager,
) -> None:
    await sub_manager.load_data()
    user: UserDto = sub_manager.middleware_data[USER_KEY]

    logger.debug(f"{format_log_user(user)} Attempted to remove duration")

    adapter = DialogDataAdapter(sub_manager.manager)
    plan = adapter.load(PlanDto)

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for duration removal")
        return

    duration_to_remove = int(sub_manager.item_id)
    new_durations = [d for d in plan.durations if d.days != duration_to_remove]
    plan.durations = new_durations
    adapter.save(plan)
    logger.info(
        f"{format_log_user(user)} Successfully removed duration "
        f"'{duration_to_remove}' days from plan"
    )


async def on_duration_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    dialog_manager.show_mode = ShowMode.EDIT
    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    logger.debug(f"{format_log_user(user)} Attempted to add new plan duration")

    if message.text is None or not (message.text.isdigit() and int(message.text) > 0):
        logger.warning(f"{format_log_user(user)} Provided invalid duration input: '{message.text}'")
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-plan-wrong-number",
        )
        return

    number = int(message.text)
    adapter = DialogDataAdapter(dialog_manager)
    plan = adapter.load(PlanDto)

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for duration input")
        return

    plan.durations.append(
        PlanDurationDto(
            days=number,
            prices=[
                PlanPriceDto(
                    currency=currency,
                    price=100,
                )
                for currency in Currency
            ],
        )
    )
    adapter.save(plan)

    logger.info(f"{format_log_user(user)} New duration '{number}' days added to plan")
    await dialog_manager.switch_to(state=RemnashopPlans.DURATIONS)


async def on_currency_selected(
    callback: CallbackQuery,
    widget: Select[Currency],
    dialog_manager: DialogManager,
    currency_selected: Currency,
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    logger.debug(f"{format_log_user(user)} Selected currency '{currency_selected}'")
    dialog_manager.dialog_data["currency_selected"] = currency_selected
    await dialog_manager.switch_to(state=RemnashopPlans.PRICE)


async def on_price_input(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    dialog_manager.show_mode = ShowMode.EDIT
    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    logger.debug(f"{format_log_user(user)} Attempted to set plan price")

    if message.text is None:
        logger.warning(f"{format_log_user(user)} Provided empty price input")
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-plan-wrong-number",
        )
        return

    try:
        new_price = Decimal(message.text)
        if new_price <= 0:
            raise InvalidOperation
    except InvalidOperation:
        logger.warning(f"{format_log_user(user)} Provided invalid price input: '{message.text}'")
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-plan-wrong-number",
        )
        return

    adapter = DialogDataAdapter(dialog_manager)
    plan = adapter.load(PlanDto)

    if not plan:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for price input")
        return

    duration_selected = dialog_manager.dialog_data.get("duration_selected")
    currency_selected = dialog_manager.dialog_data.get("currency_selected")

    if currency_selected == Currency.XTR:
        new_price = new_price.quantize(Decimal(0))
        logger.debug(f"{format_log_user(user)} Quantizing XTR price to integer: '{new_price}'")

    for duration in plan.durations:
        if duration.days == duration_selected:
            for price in duration.prices:
                if price.currency == currency_selected:
                    price.price = new_price
                    logger.debug(
                        f"{format_log_user(user)} Updated price for duration '{duration.days}' "
                        f"and currency '{currency_selected}' to '{new_price}'"
                    )
                    break
            break

    adapter.save(plan)
    await dialog_manager.switch_to(state=RemnashopPlans.PRICES)


async def on_confirm_plan(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    logger.debug(f"{format_log_user(user)} Attempted to confirm and create plan")

    adapter = DialogDataAdapter(dialog_manager)
    plan_data = adapter.load(PlanDto)

    if not plan_data:
        logger.error(f"{format_log_user(user)} Failed to load PlanDto for plan confirmation")
        return

    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]

    if plan_data.type == PlanType.DEVICES:
        plan_data.traffic_limit = None
    elif plan_data.type == PlanType.TRAFFIC:
        plan_data.device_limit = None
    elif plan_data.type == PlanType.BOTH:
        pass
    else:
        plan_data.traffic_limit = None
        plan_data.device_limit = None

    if plan_data.availability != PlanAvailability.ALLOWED:
        plan_data.allowed_user_ids = None

    if await container.services.plan.get_by_name(name=plan_data.name):
        logger.warning(
            f"{format_log_user(user)} Plan with name '{plan_data.name}' "
            f"already exists during confirmation. Aborting plan creation"
        )
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-plan-wrong-name",
        )
        return

    plan = await container.services.plan.create(plan_data)
    logger.info(
        f"{format_log_user(user)} Plan '{plan.name}' created successfully. Plan ID: '{plan.id}'"
    )
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=RemnashopPlans.MAIN)
