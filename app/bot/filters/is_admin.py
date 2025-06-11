import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.core.enums import UserRole
from app.db.models import User

logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message, user: User) -> bool:
        return user.role == UserRole.ADMIN
