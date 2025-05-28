import logging
from typing import Any, Awaitable, Callable, Optional

from aiogram.types import Message
from aiogram.types import User as AiogramUser

from app.core.enums import Command, MiddlewareEventType

from .base import EventTypedMiddleware

logger = logging.getLogger(__name__)


class GarbageMiddleware(EventTypedMiddleware):
    __event_types__ = [MiddlewareEventType.MESSAGE]

    def __init__(self) -> None:
        logger.debug("Garbage Middleware initialized")

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        aiogram_user: Optional[AiogramUser] = event.from_user

        if aiogram_user is None:
            return await handler(event, data)

        if aiogram_user.id != event.bot.id and event.text != f"/{Command.START.value.command}":
            await event.delete()
            logger.debug(f"[User:{aiogram_user.id} ({aiogram_user.full_name})] Message deleted")

        return await handler(event, data)
