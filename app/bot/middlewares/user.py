from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union

from aiogram.types import CallbackQuery, ErrorEvent, Message
from aiogram.types import User as AiogramUser

from app.bot.models import AppContainer
from app.core.constants import APP_CONTAINER_KEY, USER_KEY
from app.core.enums import MiddlewareEventType

from .base import EventTypedMiddleware

if TYPE_CHECKING:
    from app.db.models import UserDto

logger = logging.getLogger(__name__)


class UserMiddleware(EventTypedMiddleware):
    __event_types__ = [
        MiddlewareEventType.MESSAGE,
        MiddlewareEventType.CALLBACK_QUERY,
        MiddlewareEventType.ERROR,
    ]

    def __init__(self) -> None:
        logger.debug("User Middleware initialized")

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery, ErrorEvent],
        data: dict[str, Any],
    ) -> Optional[Any]:
        aiogram_user: Optional[AiogramUser] = None

        if isinstance(event, (CallbackQuery)):
            aiogram_user = event.from_user
        elif isinstance(event, (Message)):
            aiogram_user = event.from_user
        elif isinstance(event, (ErrorEvent)):
            if event.update.callback_query:
                aiogram_user = event.update.callback_query.from_user
            elif event.update.message:
                aiogram_user = event.update.message.from_user

        if aiogram_user is None or aiogram_user.is_bot:
            return await handler(event, data)

        container: AppContainer = data[APP_CONTAINER_KEY]
        user_service = container.services.user
        user: Optional[UserDto] = await user_service.get(telegram_id=aiogram_user.id)

        if user is None:
            is_dev = True if container.config.bot.dev_id == aiogram_user.id else False
            user = await user_service.create(
                aiogram_user=aiogram_user, i18n=container.i18n, is_dev=is_dev
            )

        if user.is_bot_blocked:
            await user_service.set_bot_blocked(user=user, blocked=False)

        data[USER_KEY] = user
        return await handler(event, data)
