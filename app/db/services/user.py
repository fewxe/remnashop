from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional

from aiogram.types import User as AiogramUser
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.enums import UserRole

from .. import SQLSessionContext
from ..models import User

if TYPE_CHECKING:
    from app.bot.middlewares import I18nMiddleware

logger = logging.getLogger(__name__)


class UserService:
    session_pool: async_sessionmaker[AsyncSession]

    def __init__(self, session_pool: async_sessionmaker[AsyncSession]) -> None:
        self.session_pool = session_pool

    async def create(
        self,
        aiogram_user: AiogramUser,
        i18n: I18nMiddleware,
        is_dev: bool = False,
    ) -> User:
        async with SQLSessionContext(self.session_pool) as (repository, uow):
            user = User(
                telegram_id=aiogram_user.id,
                name=aiogram_user.full_name,
                language=(
                    aiogram_user.language_code
                    if aiogram_user.language_code in i18n.locales
                    else i18n.default_locale
                ),
                role=UserRole.ADMIN if is_dev else UserRole.USER,
            )
            await uow.commit(user)
        logger.info(f"[User:{user.telegram_id} ({user.name})] Created in database")
        return user

    async def _get(
        self,
        getter: Callable[[Any], Awaitable[Optional[User]]],
        key: Any,
    ) -> Optional[User]:
        return await getter(key)

    async def get(self, telegram_id: int) -> Optional[User]:
        async with SQLSessionContext(self.session_pool) as (repository, uow):
            return await self._get(repository.users.get, telegram_id)

    async def update(self, user: User, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(user, key, value)
        async with SQLSessionContext(self.session_pool) as (repository, uow):
            await repository.users.update(telegram_id=user.telegram_id, **kwargs)

    async def set_bot_blocked(self, user: User, blocked: bool) -> None:
        async with SQLSessionContext(self.session_pool) as (repository, uow):
            await repository.users.update(telegram_id=user.telegram_id, is_bot_blocked=blocked)
        logger.info(f"[User:{user.telegram_id} ({user.name})] Set is_bot_blocked -> {blocked}")
