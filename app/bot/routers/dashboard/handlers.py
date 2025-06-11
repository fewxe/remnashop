import logging
from typing import Optional

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.api.exceptions import UnknownState

from app.bot.filters.is_admin import IsAdmin
from app.bot.middlewares.i18n import I18nFormatter
from app.bot.models import AppContainer
from app.bot.states import DashboardState
from app.db.models import UserDto

logger = logging.getLogger(__name__)
router = Router()


@router.message(IsAdmin())
async def get_user_handler(
    message: Message,
    dialog_manager: DialogManager,
    i18n_formatter: I18nFormatter,
    user: UserDto,
    container: AppContainer,
) -> None:
    logger.info(f"[User:{user.telegram_id} ({user.name})] Getting user")
    user_id: Optional[int] = None

    if message.forward_from and not message.forward_from.is_bot:
        user_id = message.forward_from.id

    elif message.text and message.text.isdigit():
        user_id = int(message.text)

    find_user: Optional[UserDto] = await container.services.user.get(user_id)
    if find_user:
        print(find_user)

    await dialog_manager.start(
        DashboardState.user,
        data={
            "id": find_user.id,
            "name": find_user.name,
            "balance": find_user.balance,
            "role": find_user.role,
        },
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
    )
