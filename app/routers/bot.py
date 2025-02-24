from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..core.bot import bot

router = Router()

async def get_start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Создать заказ", callback_data="create_order")
    builder.button(text="🔍 Мои заказы", callback_data="my_orders")
    builder.button(text="👤 Профиль", callback_data="profile")
    builder.button(
        text="🌐 Веб-приложение", 
        url="https://drilling-flow.vercel.app/webapp"
    )
    builder.adjust(2)
    return builder.as_markup()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=await get_start_keyboard()
    )

@router.callback_query(lambda c: c.data == "create_order")
async def process_create_order(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Выберите тип заказа:")
    # Здесь будет логика создания заказа

@router.callback_query(lambda c: c.data == "my_orders")
async def process_my_orders(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Ваши заказы:")
    # Здесь будет список заказов

@router.callback_query(lambda c: c.data == "profile")
async def process_profile(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Ваш профиль:")
    # Здесь будет информация о профиле 