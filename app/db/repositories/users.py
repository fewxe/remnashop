from typing import Any, Optional

from ..models import User
from .base import BaseRepository


class UsersRepository(BaseRepository):
    async def get(self, telegram_id: int) -> Optional[User]:
        return await self._get(User, User.telegram_id == telegram_id)

    async def update(self, telegram_id: int, **kwargs: Any) -> Optional[User]:
        return await self._update(
            model=User,
            conditions=[User.telegram_id == telegram_id],
            load_result=False,
            **kwargs,
        )

    async def delete(self, telegram_id: int) -> bool:
        return await self._delete(User, User.telegram_id == telegram_id)
