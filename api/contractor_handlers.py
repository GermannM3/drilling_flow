import os
import json
import uuid
import logging
from typing import Dict, Any, Optional, List, Tuple
import datetime
import sys

# Добавляем текущий каталог в sys.path для импорта модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Импортируем модели и функции для работы с базой данных
from models import User, Contractor, Order, OrderRating, ContractorStatus, SpecializationType, VerificationStatus
from database import (
    create_user,
    get_user_by_telegram_id,
    update_user,
    create_contractor, 
    get_contractor_by_telegram_id, 
    update_contractor,
    create_verification_request
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы
ADMIN_GROUP_ID = os.getenv("BOT_ADMIN_GROUP_ID", "-1002169340954")
SUPPORT_GROUP_ID = os.getenv("BOT_SUPPORT_GROUP_ID", "-1002169340954")

# Состояния для процесса регистрации
class RegistrationState:
    IDLE = "idle"
    AWAITING_FULL_NAME = "awaiting_full_name"
    AWAITING_PHONE = "awaiting_phone"
    AWAITING_EMAIL = "awaiting_email"
    AWAITING_SPECIALIZATION = "awaiting_specialization"
    AWAITING_WORK_RADIUS = "awaiting_work_radius"
    AWAITING_LOCATION = "awaiting_location"
    AWAITING_DOCUMENT = "awaiting_document"
    AWAITING_CONFIRMATION = "awaiting_confirmation"

# Временное хранилище для состояний пользователей (в реальной системе нужна БД)
user_states = {}
registration_data = {}

async def start_registration(chat_id: str, user_name: str, telegram_id: str, token: str) -> None:
    """Начинает процесс регистрации подрядчика"""
    # Проверяем, зарегистрирован ли пользователь уже
    success, result = get_contractor_by_telegram_id(telegram_id)
    
    if success:
        # Пользователь уже зарегистрирован
        status_text = "активен" if result.status == ContractorStatus.ACTIVE else "ожидает проверки"
        response_text = f"Вы уже зарегистрированы как подрядчик.\nСтатус: {status_text}\n\nИспользуйте команду /contractor_profile для просмотра вашего профиля."
        
        send_message(token, chat_id, response_text)
        return
    
    # Начинаем процесс регистрации
    response_text = f"Здравствуйте, {user_name}!\n\nДавайте начнем регистрацию вас как подрядчика в системе DrillFlow. Нам потребуется собрать некоторую информацию о вас и вашей специализации.\n\nКак вас зовут? Пожалуйста, введите ваше полное имя (ФИО)."
    
    # Устанавливаем состояние пользователя
    user_states[telegram_id] = RegistrationState.AWAITING_FULL_NAME
    registration_data[telegram_id] = {
        "telegram_id": telegram_id
    }
    
    # Отправляем сообщение
    send_message(token, chat_id, response_text)

async def process_registration_step(chat_id: str, telegram_id: str, text: str, token: str) -> None:
    """Обрабатывает шаги регистрации подрядчика"""
    if telegram_id not in user_states:
        # Пользователь не начал регистрацию
        return
    
    current_state = user_states.get(telegram_id)
    
    if current_state == RegistrationState.AWAITING_FULL_NAME:
        # Получаем полное имя
        registration_data[telegram_id]["full_name"] = text
        
        # Переходим к следующему шагу
        response_text = "Спасибо! Теперь, пожалуйста, введите ваш номер телефона в формате +7XXXXXXXXXX:"
        user_states[telegram_id] = RegistrationState.AWAITING_PHONE
        
        send_message(token, chat_id, response_text)
    
    elif current_state == RegistrationState.AWAITING_PHONE:
        # Валидация телефона (простая проверка)
        if not (text.startswith("+7") and len(text) == 12 and text[1:].isdigit()):
            response_text = "Пожалуйста, введите корректный номер телефона в формате +7XXXXXXXXXX:"
            send_message(token, chat_id, response_text)
            return
        
        # Сохраняем телефон
        registration_data[telegram_id]["phone"] = text
        
        # Переходим к следующему шагу
        response_text = "Отлично! Теперь укажите ваш email для связи:"
        user_states[telegram_id] = RegistrationState.AWAITING_EMAIL
        
        send_message(token, chat_id, response_text)
    
    elif current_state == RegistrationState.AWAITING_EMAIL:
        # Простая валидация email
        if "@" not in text or "." not in text:
            response_text = "Пожалуйста, введите корректный email адрес:"
            send_message(token, chat_id, response_text)
            return
        
        # Сохраняем email
        registration_data[telegram_id]["email"] = text
        
        # Переходим к выбору специализации
        response_text = "Укажите вашу специализацию, выбрав один из вариантов:"
        
        # Создаем инлайн-клавиатуру для выбора специализации
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🔄 Бурение", "callback_data": "spec_drilling"}
                ],
                [
                    {"text": "🚿 Канализация", "callback_data": "spec_sewerage"}
                ],
                [
                    {"text": "🔄 Бурение и канализация", "callback_data": "spec_both"}
                ]
            ]
        }
        
        user_states[telegram_id] = RegistrationState.AWAITING_SPECIALIZATION
        
        # Отправляем сообщение с клавиатурой
        send_message(token, chat_id, response_text, keyboard)
    
    elif current_state == RegistrationState.AWAITING_WORK_RADIUS:
        # Валидация радиуса работы
        try:
            radius = int(text)
            if radius <= 0 or radius > 100:
                raise ValueError("Radius out of range")
            
            # Сохраняем радиус работы
            registration_data[telegram_id]["work_radius"] = radius
            
            # Переходим к выбору местоположения
            response_text = "Пожалуйста, отправьте ваше местоположение с помощью функции Telegram (прикрепить > локация) или введите координаты в формате latitude,longitude (например: 55.7558,37.6173 для Москвы):"
            
            user_states[telegram_id] = RegistrationState.AWAITING_LOCATION
            
            send_message(token, chat_id, response_text)
        
        except ValueError:
            response_text = "Пожалуйста, введите корректное значение радиуса работы (от 1 до 100 км):"
            send_message(token, chat_id, response_text)
    
    elif current_state == RegistrationState.AWAITING_LOCATION:
        # Парсим координаты
        try:
            # Предполагаем, что пользователь ввел координаты в формате lat,lon
            lat, lon = map(float, text.split(","))
            
            # Проверяем валидность координат
            if lat < -90 or lat > 90 or lon < -180 or lon > 180:
                raise ValueError("Invalid coordinates")
            
            # Сохраняем местоположение
            registration_data[telegram_id]["location"] = {
                "lat": lat,
                "lon": lon
            }
            
            # Переходим к загрузке документов
            response_text = "Отлично! Теперь загрузите фотографию вашей техники для бурения. Это поможет нам верифицировать вас как подрядчика."
            
            user_states[telegram_id] = RegistrationState.AWAITING_DOCUMENT
            
            send_message(token, chat_id, response_text)
        
        except Exception:
            response_text = "Пожалуйста, введите корректные координаты в формате latitude,longitude (например: 55.7558,37.6173 для Москвы):"
            send_message(token, chat_id, response_text)
    
    elif current_state == RegistrationState.AWAITING_CONFIRMATION:
        # Обрабатываем подтверждение регистрации
        if text.lower() in ["да", "подтверждаю", "верно", "yes", "confirm"]:
            # Создаем подрядчика в базе данных
            try:
                # Создаем объект подрядчика
                contractor = Contractor(
                    user_id=str(uuid.uuid4()),
                    full_name=registration_data[telegram_id]["full_name"],
                    phone=registration_data[telegram_id]["phone"],
                    email=registration_data[telegram_id]["email"],
                    telegram_id=telegram_id,
                    specialization=registration_data[telegram_id]["specialization"],
                    work_radius=registration_data[telegram_id]["work_radius"],
                    location=registration_data[telegram_id]["location"],
                    status=ContractorStatus.PENDING
                )
                
                # Сохраняем в базе данных
                success, result = create_contractor(contractor)
                
                if not success:
                    logger.error(f"Failed to create contractor: {result}")
                    response_text = "Произошла ошибка при создании вашего профиля. Пожалуйста, попробуйте позже или свяжитесь с поддержкой."
                    send_message(token, chat_id, response_text)
                    return
                
                # Создаем запрос на верификацию
                verification = VerificationRequest(
                    request_id=str(uuid.uuid4()),
                    contractor_id=contractor.user_id,
                    documents=registration_data[telegram_id].get("documents", [])
                )
                
                success, result = create_verification_request(verification)
                
                if not success:
                    logger.error(f"Failed to create verification request: {result}")
                
                # Отправляем сообщение о успешной регистрации
                response_text = f"Поздравляем! Ваша регистрация в качестве подрядчика успешно завершена. Ваша заявка на верификацию отправлена модераторам и будет рассмотрена в ближайшее время.\n\nИспользуйте команду /contractor_profile для просмотра вашего профиля."
                
                # Отправляем уведомление администраторам
                admin_text = f"Новая заявка на регистрацию подрядчика!\n\nИмя: {contractor.full_name}\nТелефон: {contractor.phone}\nEmail: {contractor.email}\nСпециализация: {contractor.specialization.value}\nID: {contractor.user_id}"
                send_message(token, ADMIN_GROUP_ID, admin_text)
                
                # Сбрасываем состояния
                user_states.pop(telegram_id, None)
                registration_data.pop(telegram_id, None)
            
            except Exception as e:
                logger.error(f"Error during contractor registration: {str(e)}")
                response_text = "Произошла ошибка при обработке вашей регистрации. Пожалуйста, попробуйте позже или свяжитесь с поддержкой."
            
            send_message(token, chat_id, response_text)
        
        else:
            # Пользователь не подтвердил данные
            response_text = "Регистрация отменена. Вы можете начать процесс заново с помощью команды /register_contractor."
            
            # Сбрасываем состояния
            user_states.pop(telegram_id, None)
            registration_data.pop(telegram_id, None)
            
            send_message(token, chat_id, response_text)

async def handle_registration_callback(callback_id: str, chat_id: str, telegram_id: str, data: str, token: str) -> None:
    """Обрабатывает callback запросы в процессе регистрации"""
    if telegram_id not in user_states:
        return
    
    current_state = user_states.get(telegram_id)
    
    # Отвечаем на колбэк, чтобы убрать часы загрузки
    answer_callback_query(token, callback_id)
    
    if current_state == RegistrationState.AWAITING_SPECIALIZATION and data.startswith("spec_"):
        # Обрабатываем выбор специализации
        specialization_type = data.split("_")[1]
        
        if specialization_type == "drilling":
            registration_data[telegram_id]["specialization"] = SpecializationType.DRILLING
            spec_text = "Бурение"
        elif specialization_type == "sewerage":
            registration_data[telegram_id]["specialization"] = SpecializationType.SEWERAGE
            spec_text = "Канализация"
        else:  # both
            registration_data[telegram_id]["specialization"] = SpecializationType.BOTH
            spec_text = "Бурение и канализация"
        
        # Переходим к следующему шагу
        response_text = f"Вы выбрали специализацию: {spec_text}.\n\nТеперь укажите максимальный радиус работы в километрах (от 1 до 100):"
        
        user_states[telegram_id] = RegistrationState.AWAITING_WORK_RADIUS
        
        send_message(token, chat_id, response_text)
    
    elif current_state == RegistrationState.AWAITING_CONFIRMATION:
        if data == "confirm_registration":
            # Обрабатываем подтверждение регистрации (аналогично текстовому варианту)
            # Код аналогичен ветке AWAITING_CONFIRMATION в process_registration_step
            # для текстового подтверждения "да"
            pass
        elif data == "cancel_registration":
            # Пользователь отменил регистрацию
            response_text = "Регистрация отменена. Вы можете начать процесс заново с помощью команды /register_contractor."
            
            # Сбрасываем состояния
            user_states.pop(telegram_id, None)
            registration_data.pop(telegram_id, None)
            
            send_message(token, chat_id, response_text)

async def handle_document_upload(chat_id: str, telegram_id: str, file_id: str, token: str) -> None:
    """Обрабатывает загрузку документов (фото техники) в процессе регистрации"""
    if telegram_id not in user_states:
        return
    
    current_state = user_states.get(telegram_id)
    
    if current_state == RegistrationState.AWAITING_DOCUMENT:
        # Сохраняем информацию о документе
        if "documents" not in registration_data[telegram_id]:
            registration_data[telegram_id]["documents"] = []
        
        registration_data[telegram_id]["documents"].append({
            "file_id": file_id,
            "type": "equipment_photo",
            "uploaded_at": datetime.datetime.now().isoformat()
        })
        
        # Собираем данные для подтверждения
        full_name = registration_data[telegram_id]["full_name"]
        phone = registration_data[telegram_id]["phone"]
        email = registration_data[telegram_id]["email"]
        specialization = registration_data[telegram_id]["specialization"]
        work_radius = registration_data[telegram_id]["work_radius"]
        location = registration_data[telegram_id]["location"]
        
        spec_text = "Бурение"
        if specialization == SpecializationType.SEWERAGE:
            spec_text = "Канализация"
        elif specialization == SpecializationType.BOTH:
            spec_text = "Бурение и канализация"
        
        # Предлагаем подтвердить данные
        response_text = f"Спасибо! Проверьте введенные данные:\n\n"
        response_text += f"ФИО: {full_name}\n"
        response_text += f"Телефон: {phone}\n"
        response_text += f"Email: {email}\n"
        response_text += f"Специализация: {spec_text}\n"
        response_text += f"Радиус работы: {work_radius} км\n"
        response_text += f"Координаты: {location['lat']}, {location['lon']}\n"
        response_text += f"Загружено документов: {len(registration_data[telegram_id]['documents'])}\n\n"
        response_text += f"Все верно? Для подтверждения напишите 'Да' или нажмите кнопку ниже:"
        
        # Создаем инлайн-клавиатуру для подтверждения
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Да, подтверждаю", "callback_data": "confirm_registration"}
                ],
                [
                    {"text": "❌ Отмена", "callback_data": "cancel_registration"}
                ]
            ]
        }
        
        user_states[telegram_id] = RegistrationState.AWAITING_CONFIRMATION
        
        # Отправляем сообщение с клавиатурой
        send_message(token, chat_id, response_text, keyboard)

async def handle_location(chat_id: str, telegram_id: str, latitude: float, longitude: float, token: str) -> None:
    """Обрабатывает отправку местоположения в процессе регистрации"""
    if telegram_id not in user_states:
        return
    
    current_state = user_states.get(telegram_id)
    
    if current_state == RegistrationState.AWAITING_LOCATION:
        # Сохраняем местоположение
        registration_data[telegram_id]["location"] = {
            "lat": latitude,
            "lon": longitude
        }
        
        # Переходим к загрузке документов
        response_text = "Отлично! Теперь загрузите фотографию вашей техники для бурения. Это поможет нам верифицировать вас как подрядчика."
        
        user_states[telegram_id] = RegistrationState.AWAITING_DOCUMENT
        
        send_message(token, chat_id, response_text)

async def show_contractor_profile(chat_id: str, telegram_id: str, token: str) -> None:
    """Показывает профиль подрядчика"""
    # Получаем информацию о подрядчике
    success, contractor = get_contractor_by_telegram_id(telegram_id)
    
    if not success:
        response_text = "Вы не зарегистрированы как подрядчик. Используйте команду /register_contractor для регистрации."
        send_message(token, chat_id, response_text)
        return
    
    # Формируем текст профиля
    status_text = "Активен"
    if contractor.status == ContractorStatus.PENDING:
        status_text = "Ожидает проверки"
    elif contractor.status == ContractorStatus.BLOCKED:
        status_text = "Заблокирован"
    
    spec_text = "Бурение"
    if contractor.specialization == SpecializationType.SEWERAGE:
        spec_text = "Канализация"
    elif contractor.specialization == SpecializationType.BOTH:
        spec_text = "Бурение и канализация"
    
    response_text = f"📋 Профиль подрядчика\n\n"
    response_text += f"ФИО: {contractor.full_name}\n"
    response_text += f"Телефон: {contractor.phone}\n"
    response_text += f"Email: {contractor.email}\n"
    response_text += f"ID: {contractor.user_id}\n"
    response_text += f"Специализация: {spec_text}\n"
    response_text += f"Радиус работы: {contractor.work_radius} км\n"
    response_text += f"Статус: {status_text}\n"
    response_text += f"Рейтинг: {'⭐' * int(contractor.rating)}\n"
    response_text += f"Выполнено заказов: {contractor.completed_orders}\n"
    
    # Создаем инлайн-клавиатуру для управления профилем
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🔄 Обновить профиль", "callback_data": "update_profile"}
            ],
            [
                {"text": "📊 Мои заказы", "callback_data": "my_orders"}
            ],
            [
                {"text": "⚙️ Настройки", "callback_data": "profile_settings"}
            ]
        ]
    }
    
    # Отправляем сообщение с клавиатурой
    send_message(token, chat_id, response_text, keyboard)

# Вспомогательные функции для отправки сообщений в Telegram

def send_message(token: str, chat_id: str, text: str, reply_markup: Dict = None) -> None:
    """Отправляет сообщение в Telegram"""
    import urllib.request
    import json
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        data["reply_markup"] = reply_markup
    
    req = urllib.request.Request(
        send_url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Message sent: {result}")
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")

def answer_callback_query(token: str, callback_query_id: str, text: str = None) -> None:
    """Отвечает на callback query"""
    import urllib.request
    import json
    
    answer_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    answer_data = {
        "callback_query_id": callback_query_id
    }
    
    if text:
        answer_data["text"] = text
    
    req = urllib.request.Request(
        answer_url,
        data=json.dumps(answer_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Callback answered: {result}")
    except Exception as e:
        logger.error(f"Error answering callback: {str(e)}") 