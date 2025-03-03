import os
import json
import time
import uuid
import asyncio
import logging
import urllib.request
import urllib.parse
import traceback
import math
from typing import List, Dict, Any, Optional, Tuple

# Импортируем модели данных и функции для работы с базой данных
from models import Order, Contractor, OrderStatus, SpecializationType, ContractorStatus
from database import (
    get_contractor,
    get_order,
    list_contractors,
    update_order,
    assign_order_to_contractor,
    list_orders
)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Константы
MAX_ORDERS_PER_DAY = 2  # Максимальное количество заказов на подрядчика в день
MAX_OFFER_TIME_SECONDS = 300  # Время на принятие заказа (5 минут)
MAX_DISTANCE_KM = 50  # Максимальное расстояние для предложения заказа

# Кэш для отслеживания активных предложений
active_offers = {}  # order_id -> {contractor_id: expiration_time}
contractor_daily_orders = {}  # contractor_id -> {date: count}

def calculate_distance(loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
    """Рассчитывает расстояние между двумя точками (в км)"""
    # Используем упрощенную формулу для расчета расстояния
    lat1, lng1 = loc1.get('lat', 0), loc1.get('lng', 0)
    lat2, lng2 = loc2.get('lat', 0), loc2.get('lng', 0)
    
    # Проверяем данные на корректность
    if not all([lat1, lng1, lat2, lng2]):
        return float('inf')  # Возвращаем "бесконечность", если координаты некорректны
    
    # Формула гаверсинусов для расчета расстояния по поверхности сферы
    R = 6371  # Радиус Земли в километрах
    
    # Переводим координаты из градусов в радианы
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Разница в координатах
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # Формула гаверсинусов
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def get_today_date_str() -> str:
    """Возвращает сегодняшнюю дату в формате YYYY-MM-DD"""
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_contractor_daily_order_count(contractor_id: str) -> int:
    """Возвращает количество заказов, полученных подрядчиком сегодня"""
    today = get_today_date_str()
    
    if contractor_id not in contractor_daily_orders:
        contractor_daily_orders[contractor_id] = {}
    
    if today not in contractor_daily_orders[contractor_id]:
        contractor_daily_orders[contractor_id][today] = 0
    
    return contractor_daily_orders[contractor_id][today]

def increment_contractor_daily_order_count(contractor_id: str) -> None:
    """Увеличивает счетчик заказов подрядчика на сегодня"""
    today = get_today_date_str()
    
    if contractor_id not in contractor_daily_orders:
        contractor_daily_orders[contractor_id] = {}
    
    if today not in contractor_daily_orders[contractor_id]:
        contractor_daily_orders[contractor_id][today] = 0
    
    contractor_daily_orders[contractor_id][today] += 1

def get_eligible_contractors(order: Order) -> List[Contractor]:
    """Находит подходящих подрядчиков для заказа"""
    # Получаем всех активных подрядчиков
    contractors = list_contractors({"status": ContractorStatus.ACTIVE})
    
    eligible_contractors = []
    for contractor in contractors:
        # Проверяем специализацию
        if order.specialization != contractor.specialization and contractor.specialization != SpecializationType.BOTH:
            continue
        
        # Проверяем количество заказов на сегодня
        if get_contractor_daily_order_count(contractor.id) >= MAX_ORDERS_PER_DAY:
            continue
        
        # Проверяем расстояние (если есть координаты)
        if order.location and contractor.location:
            distance = calculate_distance(order.location, contractor.location)
            if distance > contractor.work_radius:
                continue
        
        # Добавляем подрядчика в список подходящих
        eligible_contractors.append(contractor)
    
    # Сортируем по рейтингу (от высокого к низкому)
    eligible_contractors.sort(key=lambda c: c.rating, reverse=True)
    
    return eligible_contractors

def distribute_order(order: Order, token: str) -> bool:
    """Распределяет заказ между подходящими подрядчиками"""
    logger.info(f"Starting order distribution for order_id: {order.order_id}")
    
    # Находим подходящих подрядчиков
    eligible_contractors = get_eligible_contractors(order)
    
    if not eligible_contractors:
        logger.warning(f"No eligible contractors found for order_id: {order.order_id}")
        return False
    
    logger.info(f"Found {len(eligible_contractors)} eligible contractors for order_id: {order.order_id}")
    
    # Инициализируем отслеживание предложений для этого заказа
    active_offers[order.order_id] = {}
    
    # Предлагаем заказ подрядчикам по очереди (в порядке рейтинга)
    for contractor in eligible_contractors:
        success = offer_order_to_contractor(order, contractor.id, token)
        if success:
            # Устанавливаем время истечения предложения
            expiration_time = int(time.time()) + MAX_OFFER_TIME_SECONDS
            active_offers[order.order_id][contractor.id] = expiration_time
            
            logger.info(f"Order {order.order_id} offered to contractor {contractor.id}, expires at {expiration_time}")
    
    # Запускаем фоновый процесс для отслеживания истечения предложений
    # (в реальном приложении это будет отдельный процесс или таймер)
    # В этом примере мы просто логируем информацию
    
    return True

def offer_order_to_contractor(order: Order, contractor_id: str, token: str) -> bool:
    """Предлагает заказ конкретному подрядчику"""
    # Получаем данные подрядчика
    success, contractor = get_contractor(contractor_id)
    
    if not success or not contractor:
        logger.error(f"Contractor {contractor_id} not found")
        return False
    
    # Формируем сообщение с предложением заказа
    message = f"🔔 <b>Новый заказ!</b>\n\n"
    message += f"<b>Название:</b> {order.title}\n"
    message += f"<b>Описание:</b> {order.description}\n"
    
    if order.price:
        message += f"<b>Стоимость:</b> {order.price} руб.\n"
    
    if order.address:
        message += f"<b>Адрес:</b> {order.address}\n"
    
    # Рассчитываем расстояние до заказа
    distance = None
    if order.location and contractor.location:
        distance = calculate_distance(order.location, contractor.location)
        message += f"<b>Расстояние:</b> {distance:.1f} км\n"
    
    message += f"\nУ вас есть 5 минут, чтобы принять заказ."
    
    # Создаем инлайн-клавиатуру для ответа
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Принять", "callback_data": f"accept_order_{order.order_id}"},
                {"text": "❌ Отклонить", "callback_data": f"decline_order_{order.order_id}"}
            ]
        ]
    }
    
    # Получаем chat_id по Telegram ID
    chat_id = contractor.user_id  # Предполагаем, что user_id в базе данных - это chat_id в Telegram
    
    # Отправляем сообщение
    try:
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "reply_markup": inline_keyboard
        }
        
        req = urllib.request.Request(
            send_url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Order offer sent to contractor {contractor_id}: {result}")
            return True
    
    except Exception as e:
        logger.error(f"Error sending order offer to contractor {contractor_id}: {str(e)}")
        return False

async def handle_order_response(callback_id: str, chat_id: str, user_id: str, data: str, token: str) -> None:
    """Обрабатывает ответ подрядчика на предложение заказа"""
    # Получаем contractor_id по user_id
    success, contractor = get_contractor(user_id)
    
    if not success or not contractor:
        logger.error(f"Contractor not found for user_id: {user_id}")
        await send_message(chat_id, "Ошибка: ваш профиль подрядчика не найден", token)
        return
    
    # Извлекаем order_id из данных callback
    parts = data.split('_')
    if len(parts) < 3:
        logger.error(f"Invalid callback data: {data}")
        return
    
    action = parts[0]  # accept или decline
    order_id = parts[2]  # ID заказа
    
    # Проверяем, что заказ существует
    success, order = get_order(order_id)
    
    if not success or not order:
        logger.error(f"Order {order_id} not found")
        await send_message(chat_id, "Ошибка: заказ не найден", token)
        return
    
    # Проверяем, что предложение все еще активно
    if (order_id not in active_offers or 
        contractor.id not in active_offers.get(order_id, {}) or
        active_offers[order_id][contractor.id] < int(time.time())):
        
        # Предложение истекло
        await send_message(chat_id, "Время на принятие заказа истекло.", token)
        
        # Отправляем ответ на callback query
        await answer_callback_query(callback_id, "Время на принятие заказа истекло", token)
        return
    
    # Обрабатываем ответ
    if action == "accept":
        # Принимаем заказ
        success = assign_order_to_contractor(order_id, contractor.id)
        
        if success:
            # Увеличиваем счетчик заказов на сегодня
            increment_contractor_daily_order_count(contractor.id)
            
            # Отправляем сообщение подрядчику
            await send_message(
                chat_id,
                f"✅ Вы приняли заказ: {order.title}\n\nВы можете начать выполнение заказа, когда будете готовы.",
                token,
                create_order_keyboard(order_id)
            )
            
            # Отправляем ответ на callback query
            await answer_callback_query(callback_id, "Заказ успешно принят", token)
            
            # Удаляем предложения для этого заказа
            if order_id in active_offers:
                del active_offers[order_id]
            
            # Отправляем уведомление заказчику
            # TODO: добавить уведомление заказчику о том, что его заказ принят
        else:
            await send_message(chat_id, "Ошибка при принятии заказа. Попробуйте еще раз.", token)
            await answer_callback_query(callback_id, "Ошибка при принятии заказа", token)
    
    elif action == "decline":
        # Отклоняем заказ
        await send_message(chat_id, f"Вы отклонили заказ: {order.title}", token)
        await answer_callback_query(callback_id, "Заказ отклонен", token)
        
        # Удаляем предложение для этого подрядчика
        if order_id in active_offers and contractor.id in active_offers[order_id]:
            del active_offers[order_id][contractor.id]

async def show_contractor_orders(chat_id: str, user_id: str, token: str) -> None:
    """Показывает список заказов подрядчика"""
    # Получаем contractor_id по user_id
    success, contractor = get_contractor(user_id)
    
    if not success or not contractor:
        logger.error(f"Contractor not found for user_id: {user_id}")
        await send_message(chat_id, "Ошибка: ваш профиль подрядчика не найден", token)
        return
    
    # Получаем заказы подрядчика
    orders = list_orders({"contractor_id": contractor.id})
    
    if not orders:
        await send_message(chat_id, "У вас пока нет активных заказов.", token)
        return
    
    # Формируем сообщение со списком заказов
    message = "<b>Ваши заказы:</b>\n\n"
    
    for order in orders:
        status_emoji = "🆕"
        if order.status == OrderStatus.ASSIGNED:
            status_emoji = "📋"
        elif order.status == OrderStatus.IN_PROGRESS:
            status_emoji = "🔄"
        elif order.status == OrderStatus.COMPLETED:
            status_emoji = "✅"
        elif order.status == OrderStatus.CANCELLED:
            status_emoji = "❌"
        
        message += f"{status_emoji} <b>{order.title}</b> "
        message += f"(ID: {order.order_id[:8]}...)\n"
        message += f"Статус: {order.status}\n"
        
        if order.price:
            message += f"Стоимость: {order.price} руб.\n"
        
        message += "\n"
    
    # Создаем инлайн-клавиатуру для выбора заказа
    inline_keyboard = {"inline_keyboard": []}
    
    for order in orders:
        inline_keyboard["inline_keyboard"].append([
            {"text": f"{order.title} ({order.status})", "callback_data": f"order_details_{order.order_id}"}
        ])
    
    # Добавляем кнопку "Обновить"
    inline_keyboard["inline_keyboard"].append([
        {"text": "🔄 Обновить список", "callback_data": "my_orders"}
    ])
    
    # Отправляем сообщение
    await send_message(chat_id, message, token, inline_keyboard)

async def show_order_details(chat_id: str, user_id: str, order_id: str, token: str) -> None:
    """Показывает детальную информацию о заказе"""
    # Получаем данные подрядчика
    success, contractor = get_contractor(user_id)
    
    if not success or not contractor:
        logger.error(f"Contractor not found for user_id: {user_id}")
        await send_message(chat_id, "Ошибка: ваш профиль подрядчика не найден", token)
        return
    
    # Получаем данные заказа
    success, order = get_order(order_id)
    
    if not success or not order:
        logger.error(f"Order {order_id} not found")
        await send_message(chat_id, "Ошибка: заказ не найден", token)
        return
    
    # Проверяем, что заказ принадлежит этому подрядчику
    if order.contractor_id != contractor.id:
        logger.warning(f"Contractor {contractor.id} tried to access order {order_id} belonging to another contractor")
        await send_message(chat_id, "У вас нет доступа к этому заказу.", token)
        return
    
    # Формируем детальное сообщение о заказе
    message = f"<b>Детали заказа</b>\n\n"
    message += f"<b>Название:</b> {order.title}\n"
    message += f"<b>Статус:</b> {order.status}\n"
    message += f"<b>Описание:</b> {order.description}\n"
    
    if order.price:
        message += f"<b>Стоимость:</b> {order.price} руб.\n"
    
    if order.address:
        message += f"<b>Адрес:</b> {order.address}\n"
    
    # Добавляем информацию о времени
    if order.created_at:
        created_at = time.strftime("%d.%m.%Y %H:%M", time.localtime(order.created_at))
        message += f"<b>Создан:</b> {created_at}\n"
    
    if order.status == OrderStatus.COMPLETED and order.completed_at:
        completed_at = time.strftime("%d.%m.%Y %H:%M", time.localtime(order.completed_at))
        message += f"<b>Завершен:</b> {completed_at}\n"
    
    # Отправляем сообщение с клавиатурой, соответствующей статусу заказа
    await send_message(chat_id, message, token, create_order_keyboard(order_id, order.status))

def create_order_keyboard(order_id: str, status: OrderStatus = OrderStatus.ASSIGNED):
    """Создает клавиатуру для управления заказом в зависимости от его статуса"""
    inline_keyboard = {"inline_keyboard": []}
    
    if status == OrderStatus.ASSIGNED:
        # Заказ назначен, но еще не начат
        inline_keyboard["inline_keyboard"].append([
            {"text": "🚀 Начать выполнение", "callback_data": f"start_order_{order_id}"}
        ])
    
    elif status == OrderStatus.IN_PROGRESS:
        # Заказ в процессе выполнения
        inline_keyboard["inline_keyboard"].append([
            {"text": "✅ Завершить заказ", "callback_data": f"complete_order_{order_id}"}
        ])
    
    # Добавляем кнопку возврата к списку заказов
    inline_keyboard["inline_keyboard"].append([
        {"text": "📋 Назад к списку заказов", "callback_data": "my_orders"}
    ])
    
    return inline_keyboard

async def update_order_status(chat_id: str, user_id: str, order_id: str, new_status: OrderStatus, token: str) -> None:
    """Обновляет статус заказа"""
    # Получаем данные подрядчика
    success, contractor = get_contractor(user_id)
    
    if not success or not contractor:
        logger.error(f"Contractor not found for user_id: {user_id}")
        await send_message(chat_id, "Ошибка: ваш профиль подрядчика не найден", token)
        return
    
    # Получаем данные заказа
    success, order = get_order(order_id)
    
    if not success or not order:
        logger.error(f"Order {order_id} not found")
        await send_message(chat_id, "Ошибка: заказ не найден", token)
        return
    
    # Проверяем, что заказ принадлежит этому подрядчику
    if order.contractor_id != contractor.id:
        logger.warning(f"Contractor {contractor.id} tried to update order {order_id} belonging to another contractor")
        await send_message(chat_id, "У вас нет доступа к этому заказу.", token)
        return
    
    # Проверяем валидность перехода статуса
    if (new_status == OrderStatus.IN_PROGRESS and order.status != OrderStatus.ASSIGNED) or \
       (new_status == OrderStatus.COMPLETED and order.status != OrderStatus.IN_PROGRESS):
        logger.warning(f"Invalid status transition for order {order_id}: {order.status} -> {new_status}")
        await send_message(chat_id, "Невозможно изменить статус заказа.", token)
        return
    
    # Обновляем статус заказа
    order.status = new_status
    
    # Если заказ завершен, устанавливаем время завершения
    if new_status == OrderStatus.COMPLETED:
        order.completed_at = int(time.time())
    
    # Сохраняем изменения
    success = update_order(order)
    
    if not success:
        logger.error(f"Failed to update order {order_id} status to {new_status}")
        await send_message(chat_id, "Ошибка при обновлении статуса заказа.", token)
        return
    
    # Отправляем сообщение об успешном обновлении
    if new_status == OrderStatus.IN_PROGRESS:
        await send_message(chat_id, f"✅ Вы начали выполнение заказа: {order.title}", token)
        # Показываем детали заказа
        await show_order_details(chat_id, user_id, order_id, token)
    
    elif new_status == OrderStatus.COMPLETED:
        await send_message(chat_id, f"🎉 Поздравляем! Вы завершили заказ: {order.title}", token)
        # Показываем список заказов
        await show_contractor_orders(chat_id, user_id, token)

async def send_message(chat_id: str, text: str, token: str, reply_markup: Dict = None) -> bool:
    """Отправляет сообщение в Telegram"""
    try:
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
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Message sent: {result}")
            return True
    
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

async def answer_callback_query(callback_query_id: str, text: str, token: str) -> bool:
    """Отвечает на callback query"""
    try:
        answer_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
        data = {
            "callback_query_id": callback_query_id,
            "text": text
        }
        
        req = urllib.request.Request(
            answer_url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            logger.info(f"Callback answered: {result}")
            return True
    
    except Exception as e:
        logger.error(f"Error answering callback: {str(e)}")
        return False 