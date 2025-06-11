from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from app.bot.models.containers import AppContainer
from app.core.constants import APP_CONTAINER_KEY, USER_KEY
from app.core.enums import UserRole
from app.db.models import User


def is_admin(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: User = manager.middleware_data.get(USER_KEY)
    return user.role == UserRole.ADMIN


def is_dev(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: User = manager.middleware_data.get(USER_KEY)
    container: AppContainer = manager.middleware_data.get(APP_CONTAINER_KEY)
    return user.telegram_id == container.config.bot.dev_id
