"""
Telegram bot keyboards
"""
from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.schemas.base import ServiceTypeEnum

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔨 Создать заказ"),
                KeyboardButton(text="📋 Мои заказы")
            ],
            [
                KeyboardButton(text="👤 Профиль"),
                KeyboardButton(text="ℹ️ Помощь")
            ]
        ],
        resize_keyboard=True
    )

def get_service_keyboard() -> InlineKeyboardMarkup:
    """Get service selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    service_buttons = {
        ServiceTypeEnum.DRILLING: "🚰 Бурение скважины",
        ServiceTypeEnum.REPAIR: "🔧 Ремонт скважины",
        ServiceTypeEnum.SEWAGE: "🚽 Канализация"
    }
    
    for service_type, text in service_buttons.items():
        builder.button(
            text=text,
            callback_data=f"service_{service_type.value}"
        )
    
    builder.adjust(1)
    return builder.as_markup()

def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Get location request keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="📍 Отправить геолокацию",
                request_location=True
            )
        ]],
        resize_keyboard=True
    )

def get_order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Get order actions keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Принять", callback_data=f"accept_{order_id}")
    builder.button(text="❌ Отказаться", callback_data=f"decline_{order_id}")
    return builder.as_markup()

def get_profile_keyboard(is_contractor: bool = False) -> InlineKeyboardMarkup:
    """Get profile actions keyboard"""
    builder = InlineKeyboardBuilder()
    
    if is_contractor:
        builder.button(text="📊 Статистика", callback_data="stats")
        builder.button(text="⚙️ Настройки профиля", callback_data="settings")
        builder.button(text="🔄 Изменить статус", callback_data="toggle_status")
    else:
        builder.button(text="💼 Стать подрядчиком", callback_data="become_contractor")
        builder.button(text="📱 Изменить контакты", callback_data="edit_contacts")
    
    builder.adjust(1)
    return builder.as_markup() 