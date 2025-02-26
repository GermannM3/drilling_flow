"""
Telegram bot initialization and core functionality
"""
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(
    token=settings.TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Use Redis for state storage
storage = RedisStorage.from_url(settings.REDIS_URL)
dp = Dispatcher(storage=storage)

async def setup_webhook(bot: Bot) -> bool:
    """
    Set up webhook for the bot
    
    Args:
        bot: Telegram bot instance
        
    Returns:
        bool: True if webhook was set successfully
    """
    try:
        webhook_url = f"https://{settings.TELEGRAM_BOT_DOMAIN}/api/webhook"
        webhook_info = await bot.get_webhook_info()
        
        # Update webhook only if URL changed
        if webhook_info.url != webhook_url:
            await bot.delete_webhook()
            await bot.set_webhook(webhook_url)
            logger.info(f"Webhook set to {webhook_url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return False

async def start_polling() -> None:
    """Start bot in polling mode"""
    try:
        logger.info("Starting bot in polling mode")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting polling: {e}")
        raise

# Export all
__all__ = ["bot", "dp", "setup_webhook", "start_polling"] 