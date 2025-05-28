import logging

from aiogram import Bot, Dispatcher

from app.core.config import AppConfig

logger = logging.getLogger(__name__)


async def webhook_startup(bot: Bot, dispatcher: Dispatcher, config: AppConfig) -> None:
    url = config.bot.webhook_url
    if await bot.set_webhook(
        url=url.get_secret_value(),
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=config.bot.secret_token.get_secret_value(),
        drop_pending_updates=config.bot.drop_pending_updates,
    ):
        logger.info(f"Bot webhook set successfully")
        logger.debug(f"Webhook url: '{url.get_secret_value()}'")
    else:
        logger.error(f"Failed to set bot webhook")


async def webhook_shutdown(bot: Bot, config: AppConfig) -> None:
    if not config.bot.reset_webhook:
        return
    if await bot.delete_webhook():
        logger.info("Bot webhook deleted successfully")
    else:
        logger.error("Failed to delete bot webhook")
