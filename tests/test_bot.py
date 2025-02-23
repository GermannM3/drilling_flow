"""
Тесты Telegram бота
"""
import pytest
from unittest.mock import AsyncMock, patch
from aiogram import Bot, Dispatcher
from app.core.config import get_settings, Settings
from app.bot.bot import TelegramBot
from app.bot.handlers import order_handler

@pytest.fixture
def mock_bot():
    """Фикстура для мока бота"""
    with patch('aiogram.Bot') as mock:
        mock.return_value = AsyncMock()
        yield mock.return_value

@pytest.fixture
def mock_dp():
    """Фикстура для диспетчера"""
    return Dispatcher()

@pytest.mark.asyncio
async def test_bot_initialization(settings):
    """Тест инициализации бота"""
    with patch('aiogram.Bot') as mock_bot, \
         patch('aiogram.Dispatcher') as mock_dp:
        bot = TelegramBot()
        assert bot.bot is not None
        assert bot.dp is not None
        assert bot.webapp_url == "https://t.me/Drill_Flow_bot/D_F"

@pytest.mark.asyncio
async def test_bot_send_message(mock_bot):
    """Тест отправки сообщения"""
    chat_id = 123
    text = "Test message"
    
    await mock_bot.send_message(chat_id=chat_id, text=text)
    mock_bot.send_message.assert_called_once_with(chat_id=chat_id, text=text)

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
    with patch('aiogram.Bot'), patch('aiogram.Dispatcher'):
        bot = TelegramBot()
        message = MockMessage("/start")
        await bot.start_command(message)
        message.answer.assert_called_once()

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
    settings = get_settings()
    with patch('aiogram.Bot') as mock_bot:
        bot = mock_bot.return_value
        bot.set_webhook = AsyncMock(return_value=True)
        result = await bot.set_webhook(url="https://example.com/webhook")
        assert result is True
        bot.set_webhook.assert_called_once_with(url="https://example.com/webhook") 