import logging
from typing import Any, Awaitable, Callable, Optional, Union

from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

from app.bot.widgets.i18n_format import I18N_FORMAT_KEY
from app.core.constants import USER_KEY
from app.core.enums import Locale, MiddlewareEventType
from app.db.models import User

from .base import EventTypedMiddleware

logger = logging.getLogger(__name__)


class I18nMiddleware(EventTypedMiddleware):
    __event_types__ = [MiddlewareEventType.MESSAGE, MiddlewareEventType.CALLBACK_QUERY]

    def __init__(
        self,
        locales: dict[Locale, FluentLocalization],
        default_locale: Locale,
    ) -> None:
        self.locales = locales
        self.default_locale = default_locale
        logger.debug("I18n Middleware initialized")

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: dict[str, Any],
    ) -> Any:
        user: Optional[User] = data.get(USER_KEY)

        if user is None:
            return await handler(event, data)

        lang = user.language
        logger.debug(f"[User:{user.telegram_id} ({user.name})] Using locale: {lang}")
        locale = self.locales[lang]
        data[I18N_FORMAT_KEY] = locale.format_value
        return await handler(event, data)
