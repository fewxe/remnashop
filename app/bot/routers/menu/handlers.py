import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.api.exceptions import UnknownState

from app.bot.middlewares.i18n import I18nFormatter
from app.bot.states import MenuState
from app.db.models import UserDto

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def command_start_handler(
    message: Message,
    user: UserDto,
    dialog_manager: DialogManager,
) -> None:
    logger.info(f"[User:{user.telegram_id} ({user.name})] Started dialog")

    await dialog_manager.start(
        MenuState.main,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


@router.error(ExceptionTypeFilter(UnknownState), F.update.message.as_("message"))
async def unknown_state_error_handler(
    event: ErrorEvent,
    message: Message,
    dialog_manager: DialogManager,
    i18n_formatter: I18nFormatter,
    user: UserDto,
) -> None:
    logger.warning(f"[User:{user.telegram_id} ({user.name})] Restarting dialog")

    await message.answer(i18n_formatter("ntf-error-unknown-state"))  # TODO: notification service
    await command_start_handler(message=message, user=user, dialog_manager=dialog_manager)


@router.message(Command("test"))
async def command_test_handler(message: Message, user: UserDto) -> None:
    logger.info(f"[User:{user.telegram_id} ({user.name})] Test command executed")

    raise UnknownState("test_state")
