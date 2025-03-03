from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import traceback
import urllib
import uuid
import time
import sys
import importlib.util
from pathlib import Path

# Добавляем текущий каталог в sys.path для импорта модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Заглушка для Stripe
# import stripe
# from api.stripe_subscription import create_customer, create_payment_link, check_subscription_status

# Инициализируем Stripe API (заглушка)
# stripe_api_key = os.getenv("STRIPE_API_KEY", "")
# stripe.api_key = stripe_api_key

# Простая заглушка для проверки статуса подписки
subscription_cache = {}

# Импортируем обработчики для подрядчиков
# Используем динамический импорт в случае проблем
try:
    from contractor_handlers import (
        start_registration,
        process_registration_step,
        handle_registration_callback,
        handle_document_upload,
        handle_location,
        show_contractor_profile,
        RegistrationState,
        user_states
    )
except ImportError:
    # Пытаемся импортировать динамически
    handler_path = os.path.join(current_dir, "contractor_handlers.py")
    if os.path.exists(handler_path):
        spec = importlib.util.spec_from_file_location("contractor_handlers", handler_path)
        contractor_handlers = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(contractor_handlers)
        start_registration = contractor_handlers.start_registration
        process_registration_step = contractor_handlers.process_registration_step
        handle_registration_callback = contractor_handlers.handle_registration_callback
        handle_document_upload = contractor_handlers.handle_document_upload
        handle_location = contractor_handlers.handle_location
        show_contractor_profile = contractor_handlers.show_contractor_profile
        RegistrationState = contractor_handlers.RegistrationState
        user_states = contractor_handlers.user_states
    else:
        print(f"Не удалось найти contractor_handlers.py в {current_dir}")
        # Создаем заглушки для функций
        async def start_registration(*args, **kwargs): pass
        async def process_registration_step(*args, **kwargs): pass
        async def handle_registration_callback(*args, **kwargs): pass
        async def handle_document_upload(*args, **kwargs): pass
        async def handle_location(*args, **kwargs): pass
        async def show_contractor_profile(*args, **kwargs): pass
        class RegistrationState:
            IDLE = "IDLE"
        user_states = {}

# Импортируем обработчики для заказов
try:
    from order_handlers import (
        distribute_order,
        offer_order_to_contractor,
        handle_order_response,
        show_contractor_orders,
        show_order_details,
        update_order_status,
        OrderStatus
    )
except ImportError:
    # Пытаемся импортировать динамически
    handler_path = os.path.join(current_dir, "order_handlers.py")
    if os.path.exists(handler_path):
        spec = importlib.util.spec_from_file_location("order_handlers", handler_path)
        order_handlers = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(order_handlers)
        distribute_order = order_handlers.distribute_order
        offer_order_to_contractor = order_handlers.offer_order_to_contractor
        handle_order_response = order_handlers.handle_order_response
        show_contractor_orders = order_handlers.show_contractor_orders
        show_order_details = order_handlers.show_order_details
        update_order_status = order_handlers.update_order_status
        OrderStatus = order_handlers.OrderStatus
    else:
        print(f"Не удалось найти order_handlers.py в {current_dir}")
        # Создаем заглушки для функций
        def distribute_order(*args, **kwargs): pass
        def offer_order_to_contractor(*args, **kwargs): pass
        async def handle_order_response(*args, **kwargs): pass
        async def show_contractor_orders(*args, **kwargs): pass
        async def show_order_details(*args, **kwargs): pass
        async def update_order_status(*args, **kwargs): pass
        class OrderStatus:
            CREATED = "CREATED"
            ASSIGNED = "ASSIGNED"
            IN_PROGRESS = "IN_PROGRESS"
            COMPLETED = "COMPLETED"
            CANCELLED = "CANCELLED"

def check_subscription_status(user_id):
    """Простая заглушка для проверки статуса подписки"""
    return user_id in subscription_cache and subscription_cache[user_id].get("active", False)

# Функция для преобразования асинхронной функции в синхронную
def run_async(async_func, *args, **kwargs):
    """Запускает асинхронную функцию синхронно"""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_func(*args, **kwargs))
    loop.close()
    return result

def send_message(token, chat_id, text, reply_markup=None, parse_mode="HTML"):
    """Отправляет сообщение в Telegram"""
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
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
            print(f"Message sent: {result}")
    except Exception as e:
        print(f"Error sending message: {e}")

def answer_callback_query(token, callback_query_id, text=None):
    """Отвечает на callback query"""
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
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"Callback answered: {result}")

def show_payment_options(token, chat_id):
    """Показывает платежные опции"""
    payment_options_text = "💳 Выберите платежную систему для тестового платежа:"
    
    # Создаем инлайн-клавиатуру с платежными опциями
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "PayMaster", "callback_data": "pay_paymaster_test"}
            ],
            [
                {"text": "Redsys", "callback_data": "pay_redsys_test"}
            ]
        ]
    }
    
    # Отправляем сообщение с инлайн-клавиатурой
    send_message(token, chat_id, payment_options_text, keyboard)

def show_subscription_options(token, chat_id, user_id, user_name):
    """Показывает опции подписки"""
    # Проверяем статус текущей подписки
    has_subscription = check_subscription_status(user_id)
    
    if has_subscription:
        subscription_text = f"🔔 Ваша подписка активна!\n\nФункции премиум-доступа включены."
        
        # Создаем инлайн-клавиатуру для управления подпиской
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📋 Детали подписки", "callback_data": "subscription_details"}
                ]
            ]
        }
    else:
        subscription_text = f"💼 Подписка на премиум-функции DrillFlow\n\n"
        subscription_text += "✓ Автоматическое распределение заказов\n"
        subscription_text += "✓ Расширенная статистика\n"
        subscription_text += "✓ Приоритетный доступ к новым заказам\n"
        subscription_text += "✓ Приоритетная техподдержка\n\n"
        subscription_text += "💰 Стоимость: 499 руб/месяц\n"
        
        # Создаем инлайн-клавиатуру для выбора платежной системы
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "💳 Оформить через PayMaster", "callback_data": "pay_paymaster_subscription"}
                ],
                [
                    {"text": "💳 Оформить через Redsys", "callback_data": "pay_redsys_subscription"}
                ]
            ]
        }
    
    # Отправляем сообщение с инлайн-клавиатурой
    send_message(token, chat_id, subscription_text, keyboard)

def send_invoice(token, chat_id, provider="paymaster", is_subscription=False):
    """Отправляет инвойс для оплаты"""
    invoice_url = f"https://api.telegram.org/bot{token}/sendInvoice"
    
    # Формируем данные для инвойса в зависимости от типа платежа
    if is_subscription:
        title = "Подписка на DrillFlow Premium"
        description = "Ежемесячная подписка на премиум-функции DrillFlow"
        amount = 49900  # 499 руб. в копейках
        payload = json.dumps({"is_subscription": True})
    else:
        title = "Тестовый платеж"
        description = "Тестовый платеж для проверки системы"
        amount = 100  # 1 руб. в копейках
        payload = json.dumps({"is_subscription": False})
    
    # Настройки инвойса
    invoice_data = {
        "chat_id": chat_id,
        "title": title,
        "description": description,
        "payload": payload,
        "provider_token": os.getenv(f"{provider.upper()}_PAYMENT_TOKEN", "TEST_PAYMENT_TOKEN"),
        "currency": "RUB",
        "prices": [{"label": title, "amount": amount}],
        "need_name": True,
        "need_phone_number": True,
        "need_email": True,
        "need_shipping_address": False,
        "is_flexible": False
    }
    
    req = urllib.request.Request(
        invoice_url,
        data=json.dumps(invoice_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Invoice sent: {result}")
    except Exception as e:
        print(f"Error sending invoice: {e}")
        # В случае ошибки отправляем сообщение пользователю
        error_message = "Извините, произошла ошибка при создании платежа. Пожалуйста, попробуйте позже или обратитесь в поддержку."
        send_message(token, chat_id, error_message)

# Функции-обработчики для Vercel

def get(req, res):
    """Обработчик GET-запросов для Vercel"""
    # Получаем информацию о вебхуке
    token = os.getenv("BOT_TOKEN", "")
    webhook_url = f"https://{os.getenv('BOT_WEBHOOK_DOMAIN', 'drilling-flow.vercel.app')}/api/webhook_simple"
    
    response_data = {
        "app": "DrillFlow Bot",
        "version": "1.0.0",
        "status": "running",
        "webhook_url": webhook_url,
        "telegram_bot": "@Drill_Flow_bot",
        "updated_at": int(time.time())
    }
    
    # Пытаемся получить информацию о вебхуке от Telegram
    try:
        url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        with urllib.request.urlopen(url) as response:
            webhook_info = json.loads(response.read().decode())
            response_data["current_webhook"] = webhook_info.get("result", {}).get("url", "")
            response_data["pending_updates"] = webhook_info.get("result", {}).get("pending_update_count", 0)
    except Exception as e:
        response_data["error"] = str(e)
    
    # Отправляем ответ
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_data)
    }

def post(req, res):
    """Обработчик POST-запросов для Vercel"""
    # Получаем данные запроса
    data = req.get("body", "{}")
    if isinstance(data, str):
        try:
            update = json.loads(data)
        except:
            update = {}
    else:
        update = data
    
    # Обрабатываем полученные данные
    try:
        print(f"Received update: {update}")
        
        # Получаем токен
        token = os.getenv("BOT_TOKEN", "")
        
        # Проверяем, есть ли сообщение в обновлении
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"]
            user = update["message"].get("from", {})
            user_id = str(user.get("id", ""))
            user_name = user.get("first_name", "User")
            
            # Проверяем, находится ли пользователь в процессе регистрации
            if user_id in user_states:
                current_state = user_states.get(user_id)
                if current_state != RegistrationState.IDLE:
                    # Обрабатываем шаг регистрации
                    run_async(process_registration_step, str(chat_id), user_id, text, token)
                    return {"statusCode": 200, "body": "OK"}
            
            # Обрабатываем команды
            if text.startswith('/start'):
                # Создаем ответное сообщение
                response_text = f"Привет, {user_name}!\n\nДобро пожаловать в DrillFlow - платформу для управления буровыми работами.\n\n🔹 Заказчики могут размещать заказы\n🔹 Подрядчики могут принимать заказы\n🔹 Автоматическое распределение заказов"
                
                # Создаем физическую клавиатуру (reply keyboard)
                reply_keyboard = {
                    "keyboard": [
                        [
                            {"text": "📋 Профиль"},
                            {"text": "📦 Заказы"}
                        ],
                        [
                            {"text": "❓ Помощь"},
                            {"text": "📊 Статистика"}
                        ],
                        [
                            {"text": "💳 Тестовый платеж"},
                            {"text": "🔄 Подписка"}
                        ]
                    ],
                    "resize_keyboard": True,
                    "persistent": True
                }
                
                # Отправляем сообщение с физической клавиатурой
                send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": response_text,
                    "parse_mode": "HTML",
                    "reply_markup": reply_keyboard
                }
                
                req = urllib.request.Request(
                    send_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    print(f"Message with keyboard sent: {result}")
            
            elif text.startswith('/profile') or text == "📋 Профиль" or text == "Профиль":
                # Проверяем, зарегистрирован ли пользователь как подрядчик
                run_async(show_contractor_profile, str(chat_id), user_id, token)
            
            elif text.startswith('/register_contractor'):
                # Начинаем процесс регистрации подрядчика
                run_async(start_registration, str(chat_id), user_name, user_id, token)
            
            elif text.startswith('/my_orders') or text == "📦 Заказы" or text == "Заказы":
                # Показываем список заказов подрядчика
                run_async(show_contractor_orders, str(chat_id), user_id, token)
            
            elif text.startswith('/payment') or text == "💳 Тестовый платеж" or text == "Тестовый платеж":
                # Показываем платежные опции
                show_payment_options(token, chat_id)
            
            elif text.startswith('/subscription') or text == "🔄 Подписка" or text == "Подписка":
                # Показываем опции подписки
                show_subscription_options(token, chat_id, user_id, user_name)
            
            elif text.startswith('/help') or text == "❓ Помощь" or text == "Помощь":
                # Отправляем список команд
                response_text = "Список доступных команд:\n/start - Начать работу с ботом\n/help - Получить помощь\n/profile - Мой профиль\n/orders - Мои заказы\n/payment - Сделать тестовый платеж\n/subscription - Управление подпиской"
                
                # Отправляем сообщение
                send_message(token, chat_id, response_text)
            
            elif text.startswith('/stats') or text == "📊 Статистика" or text == "Статистика":
                # Отправляем статистику
                response_text = "Ваша статистика:\nАктивных заказов: 0\nСтатус: Подрядчик"
                
                # Отправляем сообщение
                send_message(token, chat_id, response_text)
            
            else:
                # Эхо-ответ на остальные сообщения
                response_text = f"Вы написали: {text}\n\nИспользуйте /help для получения списка команд."
                
                # Отправляем сообщение
                send_message(token, chat_id, response_text)
        
        # Обрабатываем callback-запросы (нажатия на inline-кнопки)
        elif "callback_query" in update:
            callback_query = update["callback_query"]
            callback_id = callback_query["id"]
            data = callback_query["data"]
            chat_id = callback_query["message"]["chat"]["id"]
            user = callback_query.get("from", {})
            user_id = str(user.get("id", ""))
            
            # Обрабатываем callback запросы для регистрации подрядчиков
            if data.startswith('spec_') or data in ['confirm_registration', 'cancel_registration']:
                run_async(handle_registration_callback, callback_id, str(chat_id), user_id, data, token)
            
            # Обрабатываем callback запросы для заказов
            elif data.startswith('accept_order_') or data.startswith('decline_order_'):
                run_async(handle_order_response, callback_id, str(chat_id), user_id, data, token)
            
            elif data.startswith('start_order_'):
                # Извлекаем ID заказа
                order_id = data.split('_')[-1]
                run_async(update_order_status, str(chat_id), user_id, order_id, OrderStatus.IN_PROGRESS, token)
            
            elif data.startswith('complete_order_'):
                # Извлекаем ID заказа
                order_id = data.split('_')[-1]
                run_async(update_order_status, str(chat_id), user_id, order_id, OrderStatus.COMPLETED, token)
            
            elif data == 'my_orders':
                run_async(show_contractor_orders, str(chat_id), user_id, token)
            
            elif data.startswith('order_details_'):
                # Извлекаем ID заказа
                order_id = data.split('_')[-1]
                run_async(show_order_details, str(chat_id), user_id, order_id, token)
            
            elif data == "payment":
                # Показываем платежные опции
                show_payment_options(token, chat_id)
                # Отвечаем на callback
                answer_callback_query(token, callback_id)
            
            elif data == "subscription":
                # Показываем опции подписки
                user_name = callback_query["from"].get("first_name", "User")
                show_subscription_options(token, chat_id, user_id, user_name)
                # Отвечаем на callback
                answer_callback_query(token, callback_id)
            
            elif data.startswith("pay_"):
                parts = data.split("_")
                if len(parts) >= 3:
                    provider = parts[1]
                    payment_type = parts[2]
                    is_subscription = payment_type == "subscription"
                    
                    # Отправляем инвойс для оплаты
                    send_invoice(token, chat_id, provider, is_subscription)
                    
                    # Отвечаем на callback
                    answer_callback_query(token, callback_id)
            
            else:
                # Эхо-ответ на остальные callback-запросы
                response_text = f"Выбрано: {data}"
                
                # Отправляем сообщение
                send_message(token, chat_id, response_text)
                
                # Отвечаем на callback
                answer_callback_query(token, callback_id)
        
        # Обрабатываем успешные платежи
        elif "pre_checkout_query" in update:
            pre_checkout_id = update["pre_checkout_query"]["id"]
            
            # Подтверждаем предварительную проверку платежа
            pre_checkout_url = f"https://api.telegram.org/bot{token}/answerPreCheckoutQuery"
            pre_checkout_data = {
                "pre_checkout_query_id": pre_checkout_id,
                "ok": True
            }
            
            req = urllib.request.Request(
                pre_checkout_url,
                data=json.dumps(pre_checkout_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print(f"Pre-checkout answered: {result}")
        
        # Обрабатываем информацию о платеже
        elif "message" in update and "successful_payment" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            payment_info = update["message"]["successful_payment"]
            payment_amount = payment_info["total_amount"] / 100  # Сумма в копейках, переводим в рубли
            payment_currency = payment_info["currency"]
            is_subscription = "is_subscription" in payment_info["invoice_payload"] and payment_info["invoice_payload"]["is_subscription"]
            
            # Сохраняем информацию о подписке, если это подписка
            if is_subscription:
                user_id = str(update["message"]["from"]["id"])
                subscription_cache[user_id] = {
                    "active": True,
                    "expires_at": int(time.time()) + 30 * 24 * 60 * 60,  # +30 дней
                    "payment_id": payment_info["telegram_payment_charge_id"]
                }
                response_text = f"✅ Подписка успешно оформлена!\n\n"
                response_text += f"Сумма: {payment_amount} {payment_currency}\n"
                response_text += f"Идентификатор платежа: {payment_info['telegram_payment_charge_id']}\n\n"
                response_text += f"Ваша подписка активирована. Теперь вам доступны расширенные функции DrillFlow."
            else:
                response_text = f"✅ Тестовый платеж выполнен!\n\n"
                response_text += f"Сумма: {payment_amount} {payment_currency}\n"
                response_text += f"Идентификатор платежа: {payment_info['telegram_payment_charge_id']}\n\n"
                response_text += f"Спасибо за оплату! Это учебный пример с Telegram."
            
            # Отправляем сообщение
            send_message(token, chat_id, response_text)
        
        # Обрабатываем загрузку фото
        elif "message" in update and "photo" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user = update["message"].get("from", {})
            user_id = str(user.get("id", ""))
            photos = update["message"]["photo"]
            
            if photos:
                # Берем фото с наилучшим качеством (последнее в списке)
                photo = photos[-1]
                file_id = photo["file_id"]
                
                # Передаем на обработку
                run_async(handle_document_upload, str(chat_id), user_id, file_id, token)
        
        # Обрабатываем отправку документов
        elif "message" in update and "document" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user = update["message"].get("from", {})
            user_id = str(user.get("id", ""))
            document = update["message"]["document"]
            file_id = document["file_id"]
            
            # Передаем на обработку
            run_async(handle_document_upload, str(chat_id), user_id, file_id, token)
        
        # Обрабатываем отправку местоположения
        elif "message" in update and "location" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            user = update["message"].get("from", {})
            user_id = str(user.get("id", ""))
            location = update["message"]["location"]
            latitude = location["latitude"]
            longitude = location["longitude"]
            
            # Передаем на обработку
            run_async(handle_location, str(chat_id), user_id, latitude, longitude, token)
    
    except Exception as e:
        print(f"Error processing update: {e}")
        traceback.print_exc()
    
    # Отправляем успешный ответ
    return {"statusCode": 200, "body": "OK"}

# Экспортируем функции-обработчики для Vercel
def lambda_handler(event, context):
    """Функция-обертка для AWS Lambda"""
    if event.get('httpMethod') == 'GET':
        return get(event, context)
    elif event.get('httpMethod') == 'POST':
        return post(event, context)
    else:
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }

# Функция для Vercel
def handler(req, res):
    """Функция для Vercel serverless"""
    method = req.get('method', 'GET')
    if method == 'GET':
        result = get(req, None)
        return result
    elif method == 'POST':
        result = post(req, None)
        return result
    else:
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }