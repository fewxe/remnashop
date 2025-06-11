from aiogram_dialog import DialogManager

from app.bot.models.containers import AppContainer
from app.db.models import UserDto


async def admins_getter(
    dialog_manager: DialogManager,
    container: AppContainer,
    **kwargs,
) -> dict:
    admins: list[UserDto] = await container.services.user.get_admins()
    admins_data = [{"id": admin.telegram_id, "name": admin.name} for admin in admins]
    return {"admins": admins}
