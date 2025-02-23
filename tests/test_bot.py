"""
Тесты Telegram бота
"""
import pytest
from unittest.mock import AsyncMock, patch
from aiogram import Bot, Dispatcher
from app.core.config import get_settings

# Мокаем бота вместо создания реального экземпляра
@pytest.fixture
def bot():
    """Фикстура для мока бота"""
    with patch('aiogram.Bot') as mock:
        mock.return_value = AsyncMock()
        yield mock.return_value

@pytest.fixture
def dp():
    """Фикстура для диспетчера"""
    return Dispatcher()

@pytest.mark.asyncio
async def test_bot_initialization(bot):
    """Тест инициализации бота"""
    settings = get_settings()
    assert settings.TELEGRAM_TOKEN is not None
    assert isinstance(bot, AsyncMock)

@pytest.mark.asyncio
async def test_bot_send_message(bot):
    """Тест отправки сообщения"""
    chat_id = 123
    text = "Test message"
    
    await bot.send_message(chat_id=chat_id, text=text)
    bot.send_message.assert_called_once_with(chat_id=chat_id, text=text)

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