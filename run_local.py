import os
import asyncio
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения до импорта бота
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Проверяем, что токен загружен
bot_token = os.getenv("TELEGRAM_TOKEN")
if not bot_token:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables")

from api.index import bot, dp, app, logger

async def main():
    """Запуск бота в режиме поллинга"""
    logger.info("Starting bot in polling mode...")
    
    try:
        # Удаляем вебхук перед запуском поллинга
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook removed successfully")
        
        # Запускаем поллинг
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        logger.info("Bot stopped")

if __name__ == "__main__":
    if os.getenv("USE_POLLING", "0") == "1":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
    else:
        # Запускаем FastAPI приложение
        uvicorn.run(app, host="0.0.0.0", port=8000) 