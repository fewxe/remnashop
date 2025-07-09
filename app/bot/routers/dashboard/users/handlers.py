from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from loguru import logger

from app.bot.states import DashboardUsers
from app.core.constants import APP_CONTAINER_KEY, USER_KEY
from app.core.container import AppContainer
from app.core.utils.formatters import format_log_user
from app.db.models.dto import UserDto

from .user.handlers import start_user_window


async def on_user_search(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    dialog_manager.show_mode = ShowMode.EDIT
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    if not user.is_privileged:
        return

    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    found_users: list[UserDto] = []
    search_query = None

    if message.forward_from and not message.forward_from.is_bot:
        target_telegram_id = message.forward_from.id
        logger.debug(
            f"{format_log_user(user)} Searching for user by "
            f"forwarded message ID '{target_telegram_id}'"
        )
        search_query = str(target_telegram_id)
        single_user = await container.services.user.get(telegram_id=target_telegram_id)
        if single_user:
            found_users.append(single_user)
    elif message.text:
        search_query = message.text.strip()
        if search_query.isdigit():
            target_telegram_id = int(search_query)
            logger.debug(
                f"{format_log_user(user)} Searching for user by Telegram ID '{target_telegram_id}'"
            )
            single_user = await container.services.user.get(telegram_id=target_telegram_id)
            if single_user:
                found_users.append(single_user)
        else:
            logger.debug(
                f"{format_log_user(user)} Searching for user by partial name '{search_query}'"
            )
            found_users = await container.services.user.get_by_partial_name(query=search_query)

    if not found_users:
        logger.info(f"{format_log_user(user)} User search for '{search_query}' yielded no results")
        await container.services.notification.notify_user(
            user=user,
            text_key="ntf-user-not-found",
        )
        return
    elif len(found_users) == 1:
        target_user = found_users[0]
        logger.info(
            f"{format_log_user(user)} Successfully searched "
            f"for single user {format_log_user(target_user)}"
        )
        await start_user_window(manager=dialog_manager, target_telegram_id=target_user.telegram_id)
    else:
        logger.info(
            f"{format_log_user(user)} User search for '{search_query}' "
            f"found {len(found_users)} results. Proceeding to selection state"
        )

        await dialog_manager.start(
            state=DashboardUsers.SEARCH_RESULTS,
            data={"found_users": [found_user.model_dump_json() for found_user in found_users]},
        )


async def on_user_selected(
    callback: CallbackQuery,
    widget: Select[int],
    dialog_manager: DialogManager,
    user_selected: int,
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    logger.debug(f"[{format_log_user(user)}] User '{user_selected}' selected")
    await start_user_window(manager=dialog_manager, target_telegram_id=user_selected)


async def on_unblock_all(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    container: AppContainer = dialog_manager.middleware_data[APP_CONTAINER_KEY]
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    blocked_users = await container.services.user.get_blocked_users()

    for blocked_user in blocked_users:
        await container.services.user.set_block(user=blocked_user, blocked=False)

    logger.warning(f"{format_log_user(user)} Unblocked all users")
    await dialog_manager.start(state=DashboardUsers.BLACKLIST, mode=StartMode.RESET_STACK)
