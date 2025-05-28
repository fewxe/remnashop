from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fluent.runtime import FluentLocalization, FluentResourceLoader

from app.bot.middlewares import I18nMiddleware
from app.core.constants import RESOURCE_I18N

if TYPE_CHECKING:
    from app.core.config import AppConfig

logger = logging.getLogger(__name__)


def create_i18n_middleware(config: AppConfig) -> I18nMiddleware:
    loader = FluentResourceLoader(f"{config.i18n.locales_dir}/{{locale}}")
    locales = {
        locale: FluentLocalization(
            [locale, config.i18n.default_locale],
            RESOURCE_I18N,
            loader,
        )
        for locale in config.i18n.locales
    }
    logger.debug(f"Available locales: {list(locales.keys())}")
    return I18nMiddleware(locales, config.i18n.default_locale)
