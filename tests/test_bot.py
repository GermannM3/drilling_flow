import pytest
from unittest.mock import AsyncMock, patch
from app.bot.main import bot, dp
from app.bot.handlers import start_handler, order_handler
from app.core.config import Settings

class MockMessage:
    """Мок объекта сообщения Telegram"""
    def __init__(self, text, user_id=123, chat_id=123):
        self.text = text
        self.from_user = type('User', (), {'id': user_id})
        self.chat = type('Chat', (), {'id': chat_id})
        self.answer = AsyncMock()

@pytest.mark.asyncio
async def test_start_command():
    """Тест команды /start"""
    message = MockMessage("/start")
    await start_handler(message)
    message.answer.assert_called_once()
    assert "Добро пожаловать" in message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_order_creation():
    """Тест создания заказа"""
    message = MockMessage("/order")
    with patch('app.bot.handlers.create_order') as mock_create:
        mock_create.return_value = {"id": 1, "status": "created"}
        await order_handler(message)
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_bot_webhook():
    """Тест установки webhook"""
    settings = Settings()
    with patch('aiogram.Bot.set_webhook') as mock_webhook:
        mock_webhook.return_value = True
        result = await bot.set_webhook(settings.BOT_WEBHOOK_URL)
        assert result is True
        mock_webhook.assert_called_with(settings.BOT_WEBHOOK_URL) 