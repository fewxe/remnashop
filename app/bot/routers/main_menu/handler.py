import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode

from app.core.config import AppConfig
from app.db.models import User

from .dialog import MainMenuState

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def command_start_handler(
    message: Message,
    config: AppConfig,
    dialog_manager: DialogManager,
    user: User,
) -> None:
    logger.info(f"[User:{user.telegram_id} ({user.name})] Opened main menu")
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND

    await dialog_manager.start(
        MainMenuState.main_menu,
        mode=StartMode.RESET_STACK,
    )
