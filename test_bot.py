import asyncio
from app.core.bot import bot, dp
from app.core.config import get_settings

async def test_bot():
    """Тестирование бота"""
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"Бот успешно запущен: @{bot_info.username}")
        
        # Проверяем webhook
        webhook_info = await bot.get_webhook_info()
        print(f"Webhook URL: {webhook_info.url}")
        
        # Устанавливаем webhook
        settings = get_settings()
        webhook_url = f"{settings.BOT_WEBHOOK_DOMAIN}/webhook"
        await bot.set_webhook(url=webhook_url)
        print(f"Webhook установлен: {webhook_url}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_bot()) 