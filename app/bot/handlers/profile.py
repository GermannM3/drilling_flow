"""
Обработчики команд для управления профилем пользователя
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.bot.keyboards import get_profile_keyboard, get_main_keyboard
from app.services.users import UserService
from app.schemas.base import UserRoleEnum

router = Router(name="profile")

class ProfileStates(StatesGroup):
    """Состояния редактирования профиля"""
    entering_company = State()
    entering_description = State()
    entering_radius = State()
    entering_specializations = State()

@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message, user_service: UserService):
    """Показать профиль пользователя"""
    user = await user_service.get_user(str(message.from_user.id))
    if not user:
        await message.answer("Ошибка: профиль не найден")
        return
        
    profile_text = f"👤 Профиль\n\n"
    profile_text += f"Имя: {user.first_name}\n"
    profile_text += f"Username: @{user.username}\n"
    profile_text += f"Роль: {'Подрядчик' if user.role == UserRoleEnum.CONTRACTOR else 'Клиент'}\n"
    
    if user.role == UserRoleEnum.CONTRACTOR:
        contractor = await user_service.get_contractor_profile(user.id)
        if contractor:
            profile_text += f"\n💼 Информация подрядчика:\n"
            profile_text += f"Компания: {contractor.company_name or 'Не указано'}\n"
            profile_text += f"Описание: {contractor.description or 'Не указано'}\n"
            profile_text += f"Радиус работы: {contractor.work_radius_km or 'Не указано'} км\n"
            profile_text += f"Специализации: {', '.join(contractor.specializations) or 'Не указано'}\n"
            profile_text += f"Статус: {'Доступен' if contractor.is_available else 'Недоступен'}\n"
            if user.rating:
                profile_text += f"Рейтинг: {'⭐' * round(user.rating)}\n"
    
    await message.answer(
        profile_text,
        reply_markup=get_profile_keyboard(user.role == UserRoleEnum.CONTRACTOR)
    )

@router.callback_query(F.data == "become_contractor")
async def start_contractor_registration(callback: CallbackQuery, state: FSMContext):
    """Начать регистрацию подрядчика"""
    await state.set_state(ProfileStates.entering_company)
    await callback.message.answer(
        "Для регистрации в качестве подрядчика, укажите название вашей компании:"
    )
    await callback.answer()

@router.message(ProfileStates.entering_company)
async def process_company_name(message: Message, state: FSMContext):
    """Обработка ввода названия компании"""
    await state.update_data(company_name=message.text)
    await state.set_state(ProfileStates.entering_description)
    await message.answer(
        "Опишите вашу компанию и опыт работы:"
    )

@router.message(ProfileStates.entering_description)
async def process_description(message: Message, state: FSMContext):
    """Обработка ввода описания"""
    await state.update_data(description=message.text)
    await state.set_state(ProfileStates.entering_radius)
    await message.answer(
        "Укажите максимальный радиус работы в километрах (например: 50):"
    )

@router.message(ProfileStates.entering_radius)
async def process_radius(message: Message, state: FSMContext):
    """Обработка ввода радиуса работы"""
    try:
        radius = float(message.text)
        if radius <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите положительное число")
        return
        
    await state.update_data(work_radius_km=radius)
    await state.set_state(ProfileStates.entering_specializations)
    await message.answer(
        "Укажите ваши специализации через запятую (например: бурение, ремонт, канализация):"
    )

@router.message(ProfileStates.entering_specializations)
async def process_specializations(
    message: Message,
    state: FSMContext,
    user_service: UserService
):
    """Обработка ввода специализаций и создание профиля подрядчика"""
    specializations = [s.strip().lower() for s in message.text.split(",")]
    data = await state.get_data()
    
    try:
        await user_service.create_contractor_profile(
            user_id=message.from_user.id,
            company_name=data["company_name"],
            description=data["description"],
            work_radius_km=data["work_radius_km"],
            specializations=specializations
        )
        
        await message.answer(
            "✅ Профиль подрядчика успешно создан!\n"
            "Теперь вы можете принимать заказы.",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при создании профиля: {str(e)}",
            reply_markup=get_main_keyboard()
        )
    
    await state.clear()

@router.callback_query(F.data == "toggle_status")
async def toggle_contractor_status(callback: CallbackQuery, user_service: UserService):
    """Переключить статус доступности подрядчика"""
    user = await user_service.get_user(str(callback.from_user.id))
    if not user or user.role != UserRoleEnum.CONTRACTOR:
        await callback.answer("Ошибка: профиль подрядчика не найден")
        return
        
    contractor = await user_service.get_contractor_profile(user.id)
    if not contractor:
        await callback.answer("Ошибка: профиль подрядчика не найден")
        return
        
    is_available = await user_service.toggle_contractor_status(contractor.id)
    await callback.answer(
        f"Статус изменен: {'Доступен' if is_available else 'Недоступен'}"
    )
    await show_profile(callback.message, user_service) 