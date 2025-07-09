from typing import Any, Union, cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, SubManager
from aiogram_dialog.widgets.kbd import Button, Select
from loguru import logger

from app.bot.states import DashboardUser, MainMenu
from app.core.constants import APP_CONTAINER_KEY, USER_KEY
from app.core.container import AppContainer
from app.core.enums import MessageEffect, UserRole
from app.core.utils.formatters import format_log_user
from app.db.models.dto import UserDto


async def reset_user_dialog(dialog_manager: DialogManager, target_user: UserDto) -> None:
    logger.debug(f"Attempting to reset dialog stack for user {format_log_user(target_user)}")
    bg_manager = dialog_manager.bg(
        user_id=target_user.telegram_id,
        chat_id=target_user.telegram_id,
    )
    await bg_manager.start(
        state=MainMenu.MAIN,
        mode=StartMode.RESET_STACK,
    )
    logger.debug(f"Dialog stack for user {format_log_user(target_user)} reset successfully")


async def handle_role_switch_preconditions(
    user: UserDto,
    target_user: UserDto,
    container: AppContainer,
    manager: Union[DialogManager, SubManager],
) -> bool:
    if target_user.telegram_id == user.telegram_id:
        logger.debug(f"{format_log_user(user)} Attempted to switch role to self")
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-user-switch-role-self",
            message_effect=MessageEffect.POOP,
        )
        return True

    if target_user.telegram_id == container.config.bot.dev_id:
        logger.critical(f"{format_log_user(user)} Attempted to modify role of SUPER DEV")

        await container.services.user.set_role(user=user, role=UserRole.USER)
        await container.services.user.set_block(user=user, blocked=True)
        logger.warning(f"[{format_log_user(user)}] Demoted and blocked")

        await manager.start(state=MainMenu.MAIN, mode=StartMode.RESET_STACK)
        await container.services.notification.notify_super_dev(
            dev=await container.services.user.get(telegram_id=container.config.bot.dev_id),
            text_key="ntf-user-switch-role-dev",
            id=str(user.telegram_id),
            name=user.name,
        )
        return True

    return False


async def start_user_window(
    manager: Union[DialogManager, SubManager],
    target_telegram_id: int,
) -> None:
    await manager.start(
        state=DashboardUser.MAIN,
        data={"target_telegram_id": target_telegram_id},
        mode=StartMode.RESET_STACK,
    )


async def on_block_toggle(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    start_data = cast(dict[str, Any], dialog_manager.start_data)

    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    target_telegram_id = start_data["target_telegram_id"]
    target_user = await container.services.user.get(telegram_id=target_telegram_id)

    if not target_user:
        logger.warning(
            f"[{format_log_user(user)}] Attempted to toggle block status "
            f"for non-existent user with ID '{target_telegram_id}'"
        )
        return

    blocked = not target_user.is_blocked

    if target_user.telegram_id == user.telegram_id:
        logger.info(f"{format_log_user(user)} Attempted to block to self")
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-user-block-self",
            message_effect=MessageEffect.POOP,
        )
        return

    if target_user.telegram_id == container.config.bot.dev_id:
        logger.critical(f"{format_log_user(user)} Attempted to block of SUPER DEV")

        await container.services.user.set_role(user=user, role=UserRole.USER)
        await container.services.user.set_block(user=user, blocked=True)
        logger.warning(f"[{format_log_user(user)}] Demoted and blocked")

        await dialog_manager.start(state=MainMenu.MAIN, mode=StartMode.RESET_STACK)
        await container.services.notification.notify_super_dev(
            dev=await container.services.user.get(telegram_id=container.config.bot.dev_id),
            text_key="ntf-user-block-dev",
            id=user.telegram_id,
            name=user.name,
        )
        return

    await container.services.user.set_block(user=target_user, blocked=blocked)
    await reset_user_dialog(dialog_manager, target_user)
    logger.info(
        f"[{format_log_user(user)}] Successfully {'blocked' if blocked else 'unblocked'} "
        f"user {format_log_user(target_user)}"
    )


async def on_role_selected(
    callback: CallbackQuery,
    widget: Select[UserRole],
    dialog_manager: DialogManager,
    selected_role: UserRole,
) -> None:
    start_data = cast(dict[str, Any], dialog_manager.start_data)

    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    target_telegram_id = start_data["target_telegram_id"]
    target_user = await container.services.user.get(telegram_id=target_telegram_id)

    if not target_user:
        logger.warning(
            f"[{format_log_user(user)}] Attempted to change role "
            f"for non-existent user with ID '{target_telegram_id}'"
        )
        return

    if await handle_role_switch_preconditions(user, target_user, container, dialog_manager):
        logger.info(
            f"[{format_log_user(user)}] Role change for "
            f"{format_log_user(target_user)} to '{selected_role}' aborted due to pre-conditions"
        )
        return

    await container.services.user.set_role(user=target_user, role=selected_role)
    await reset_user_dialog(dialog_manager, target_user)
    logger.info(
        f"[{format_log_user(user)}] Successfully changed role for "
        f"{format_log_user(target_user)} to '{selected_role}'"
    )
