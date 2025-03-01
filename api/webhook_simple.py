from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import traceback
import uuid
# Заглушка для Stripe
# import stripe
# from api.stripe_subscription import create_customer, create_payment_link, check_subscription_status

# Инициализируем Stripe API (заглушка)
# stripe_api_key = os.getenv("STRIPE_API_KEY", "")
# stripe.api_key = stripe_api_key

# Простая заглушка для проверки статуса подписки
subscription_cache = {}

def check_subscription_status(user_id):
    """Простая заглушка для проверки статуса подписки"""
    return user_id in subscription_cache and subscription_cache[user_id].get("active", False)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Получаем информацию о вебхуке
        token = os.getenv("TELEGRAM_TOKEN", "")
        webhook_url = f"https://{os.getenv('BOT_WEBHOOK_DOMAIN', 'drilling-flow.vercel.app')}/webhook"
        
        response_data = {
            "status": "webhook endpoint is working",
            "webhook_url": webhook_url
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
        
        self.wfile.write(json.dumps(response_data).encode())
    
    def do_POST(self):
        # Получаем данные запроса
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Отправляем успешный ответ
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('OK'.encode())
        
        # Обрабатываем полученные данные
        try:
            update = json.loads(post_data.decode())
            print(f"Received update: {update}")
            
            # Получаем токен
            token = os.getenv("TELEGRAM_TOKEN", "")
            
            # Проверяем, есть ли сообщение в обновлении
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]
                user_name = update["message"]["from"].get("first_name", "пользователь")
                user_id = update["message"]["from"]["id"]
                
                # Формируем ответ в зависимости от команды
                if text == "/start":
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
                    
                    # Создаем инлайн-клавиатуру для дополнительных функций
                    inline_keyboard = {
                        "inline_keyboard": [
                            [
                                {"text": "📋 Профиль", "callback_data": "profile"},
                                {"text": "📦 Заказы", "callback_data": "orders"}
                            ],
                            [
                                {"text": "❓ Помощь", "callback_data": "help"},
                                {"text": "📊 Статистика", "callback_data": "stats"}
                            ],
                            [
                                {"text": "💳 Тестовый платеж", "callback_data": "payment"}
                            ],
                            [
                                {"text": "🔄 Подписка", "callback_data": "subscription"}
                            ]
                        ]
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
                    
                    return
                
                # Обработка текстовых команд с физической клавиатуры
                elif text == "📋 Профиль" or text == "/profile":
                    response_text = f"Профиль пользователя {user_name}\nID: {update['message']['from']['id']}\nСтатус: Активен"
                    
                    # Проверяем статус подписки
                    has_subscription = False
                    try:
                        subscription_status = check_subscription_status(user_id)
                        if isinstance(subscription_status, bool):
                            has_subscription = subscription_status
                    except Exception as e:
                        print(f"Ошибка при проверке подписки: {e}")
                    
                    if has_subscription:
                        response_text += "\n\n✅ У вас есть активная подписка!"
                    else:
                        response_text += "\n\n❌ У вас нет активной подписки. Используйте команду /subscription для оформления."
                
                elif text == "📦 Заказы" or text == "/orders":
                    # Проверяем статус подписки
                    has_subscription = False
                    try:
                        subscription_status = check_subscription_status(user_id)
                        if isinstance(subscription_status, bool):
                            has_subscription = subscription_status
                    except Exception as e:
                        print(f"Ошибка при проверке подписки: {e}")
                        
                    if has_subscription:
                        response_text = "У вас пока нет активных заказов."
                    else:
                        response_text = "❌ Для доступа к заказам требуется активная подписка.\n\nИспользуйте команду /subscription для оформления."
                
                elif text == "❓ Помощь" or text == "/help":
                    response_text = "Список доступных команд:\n/start - начать работу с ботом\n/help - показать справку\n/profile - ваш профиль\n/orders - ваши заказы\n/payment - сделать тестовый платеж\n/subscription - управление подпиской"
                
                elif text == "📊 Статистика":
                    response_text = "Ваша статистика:\nЗаказов выполнено: 0\nРейтинг: ⭐⭐⭐⭐⭐"
                
                elif text == "💳 Тестовый платеж" or text == "/payment":
                    # Показываем выбор платежной системы
                    self.show_payment_options(token, chat_id)
                    return
                
                elif text == "🔄 Подписка" or text == "/subscription":
                    # Проверяем статус подписки
                    has_subscription = False
                    try:
                        subscription_status = check_subscription_status(user_id)
                        if isinstance(subscription_status, bool):
                            has_subscription = subscription_status
                    except Exception as e:
                        print(f"Ошибка при проверке подписки: {e}")
                    
                    if has_subscription:
                        response_text = "✅ У вас уже есть активная подписка!\n\nВаш статус: Активен\nТип: Месячная\n\nПодписка автоматически продлевается в конце периода."
                    else:
                        # Показываем опции подписки
                        self.show_subscription_options(token, chat_id, user_id, user_name)
                        return
                
                else:
                    response_text = f"Вы написали: {text}\n\nИспользуйте /help для получения списка команд."
                
                # Отправляем ответ
                send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": response_text,
                    "parse_mode": "HTML"
                }
                
                req = urllib.request.Request(
                    send_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    print(f"Message sent: {result}")
            
            # Обработка колбэков от инлайн-кнопок
            elif "callback_query" in update:
                callback_id = update["callback_query"]["id"]
                chat_id = update["callback_query"]["message"]["chat"]["id"]
                data = update["callback_query"]["data"]
                user_name = update["callback_query"]["from"].get("first_name", "пользователь")
                user_id = update["callback_query"]["from"]["id"]
                
                # Формируем ответ в зависимости от данных колбэка
                if data == "profile":
                    response_text = f"Профиль пользователя {user_name}\nID: {update['callback_query']['from']['id']}\nСтатус: Активен"
                    
                    # Проверяем статус подписки
                    has_subscription = False
                    try:
                        subscription_status = check_subscription_status(user_id)
                        if isinstance(subscription_status, bool):
                            has_subscription = subscription_status
                    except Exception as e:
                        print(f"Ошибка при проверке подписки: {e}")
                    
                    if has_subscription:
                        response_text += "\n\n✅ У вас есть активная подписка!"
                    else:
                        response_text += "\n\n❌ У вас нет активной подписки. Используйте команду /subscription для оформления."
                    
                elif data == "orders":
                    # Проверяем статус подписки
                    has_subscription = False
                    try:
                        subscription_status = check_subscription_status(user_id)
                        if isinstance(subscription_status, bool):
                            has_subscription = subscription_status
                    except Exception as e:
                        print(f"Ошибка при проверке подписки: {e}")
                        
                    if has_subscription:
                        response_text = "У вас пока нет активных заказов."
                    else:
                        response_text = "❌ Для доступа к заказам требуется активная подписка.\n\nИспользуйте команду /subscription для оформления."
                
                elif data == "help":
                    response_text = "Раздел помощи. Здесь будет информация о том, как пользоваться ботом."
                elif data == "stats":
                    response_text = "Ваша статистика:\nЗаказов выполнено: 0\nРейтинг: ⭐⭐⭐⭐⭐"
                elif data == "payment":
                    # Отвечаем на колбэк
                    self.answer_callback_query(token, callback_id)
                    # Показываем выбор платежной системы
                    self.show_payment_options(token, chat_id)
                    return
                elif data == "payment_paymaster":
                    # Отвечаем на колбэк
                    self.answer_callback_query(token, callback_id)
                    # Вызываем метод создания счета на оплату через PayMaster
                    self.send_invoice(token, chat_id, "paymaster")
                    return
                elif data == "payment_redsys":
                    # Отвечаем на колбэк
                    self.answer_callback_query(token, callback_id)
                    # Вызываем метод создания счета на оплату через Redsys
                    self.send_invoice(token, chat_id, "redsys")
                    return
                elif data == "subscription":
                    # Отвечаем на колбэк
                    self.answer_callback_query(token, callback_id)
                    
                    # Проверяем статус подписки
                    has_subscription = False
                    try:
                        subscription_status = check_subscription_status(user_id)
                        if isinstance(subscription_status, bool):
                            has_subscription = subscription_status
                    except Exception as e:
                        print(f"Ошибка при проверке подписки: {e}")
                    
                    if has_subscription:
                        response_text = "✅ У вас уже есть активная подписка!\n\nВаш статус: Активен\nТип: Месячная\n\nПодписка автоматически продлевается в конце периода."
                    else:
                        # Показываем опции подписки
                        self.show_subscription_options(token, chat_id, user_id, user_name)
                        return
                
                elif data == "subscribe_stripe":
                    # Удаляем эту опцию, так как Stripe недоступен в России
                    self.answer_callback_query(token, callback_id)
                    response_text = "К сожалению, Stripe недоступен в России. Пожалуйста, выберите другой способ оплаты."
                    
                    # Отправляем сообщение
                    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                    data = {
                        "chat_id": chat_id,
                        "text": response_text,
                        "parse_mode": "HTML"
                    }
                    
                    req = urllib.request.Request(
                        send_url,
                        data=json.dumps(data).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    with urllib.request.urlopen(req) as response:
                        result = json.loads(response.read().decode())
                        print(f"Message sent: {result}")
                
                elif data == "subscribe_paymaster":
                    # Отвечаем на колбэк
                    self.answer_callback_query(token, callback_id)
                    
                    try:
                        # Генерируем ID подписки
                        subscription_id = f"paymaster_{str(uuid.uuid4())}"
                        
                        # Сохраняем информацию о подписке в кэш
                        subscription_cache[user_id] = {
                            "subscription_id": subscription_id,
                            "active": True,
                            "provider": "PayMaster"
                        }
                        
                        # Отправляем счет на оплату через PayMaster
                        self.send_invoice(token, chat_id, "paymaster", is_subscription=True)
                    except Exception as e:
                        response_text = f"Произошла ошибка при оформлении подписки: {str(e)}"
                        
                        # Отправляем сообщение
                        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                        data = {
                            "chat_id": chat_id,
                            "text": response_text,
                            "parse_mode": "HTML"
                        }
                        
                        req = urllib.request.Request(
                            send_url,
                            data=json.dumps(data).encode('utf-8'),
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        with urllib.request.urlopen(req) as response:
                            result = json.loads(response.read().decode())
                            print(f"Message sent: {result}")
                
                elif data == "subscribe_redsys":
                    # Отвечаем на колбэк
                    self.answer_callback_query(token, callback_id)
                    
                    try:
                        # Генерируем ID подписки
                        subscription_id = f"redsys_{str(uuid.uuid4())}"
                        
                        # Сохраняем информацию о подписке в кэш
                        subscription_cache[user_id] = {
                            "subscription_id": subscription_id,
                            "active": True,
                            "provider": "Redsys"
                        }
                        
                        # Отправляем счет на оплату через Redsys
                        self.send_invoice(token, chat_id, "redsys", is_subscription=True)
                    except Exception as e:
                        response_text = f"Произошла ошибка при оформлении подписки: {str(e)}"
                        
                        # Отправляем сообщение
                        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                        data = {
                            "chat_id": chat_id,
                            "text": response_text,
                            "parse_mode": "HTML"
                        }
                        
                        req = urllib.request.Request(
                            send_url,
                            data=json.dumps(data).encode('utf-8'),
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        with urllib.request.urlopen(req) as response:
                            result = json.loads(response.read().decode())
                            print(f"Message sent: {result}")
                
                else:
                    response_text = f"Выбрано: {data}"
                
                # Отвечаем на колбэк, если еще не ответили
                if data not in ["payment", "payment_paymaster", "payment_redsys", "subscription", "subscribe_stripe", "subscribe_paymaster", "subscribe_redsys"]:
                    self.answer_callback_query(token, callback_id)
                
                # Отправляем сообщение
                send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": response_text,
                    "parse_mode": "HTML"
                }
                
                req = urllib.request.Request(
                    send_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    print(f"Message sent: {result}")
            
            # Обработка pre-checkout запросов - необходимо для проведения платежей
            elif "pre_checkout_query" in update:
                pre_checkout_query_id = update["pre_checkout_query"]["id"]
                
                # Подтверждаем предварительную проверку платежа
                answer_url = f"https://api.telegram.org/bot{token}/answerPreCheckoutQuery"
                answer_data = {
                    "pre_checkout_query_id": pre_checkout_query_id,
                    "ok": True
                }
                
                req = urllib.request.Request(
                    answer_url,
                    data=json.dumps(answer_data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    print(f"Pre-checkout query answered: {result}")
            
            # Обработка успешных платежей
            elif "message" in update and "successful_payment" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                payment_info = update["message"]["successful_payment"]
                user_id = update["message"]["from"]["id"]
                
                # Проверяем, была ли это оплата подписки
                payload = payment_info.get("invoice_payload", "")
                is_subscription = payload.startswith("subscription_")
                
                # Отправляем подтверждение успешного платежа
                payment_amount = payment_info["total_amount"] / 100  # Переводим в валюту (копейки -> рубли)
                payment_currency = payment_info["currency"]
                
                if is_subscription:
                    # Активируем подписку для пользователя
                    subscription_cache[user_id] = {
                        "active": True,
                        "subscription_id": payload,
                        "payment_id": payment_info['telegram_payment_charge_id']
                    }
                    
                    response_text = f"✅ Подписка успешно оформлена!\n\n"
                    response_text += f"Сумма: {payment_amount} {payment_currency}\n"
                    response_text += f"Идентификатор платежа: {payment_info['telegram_payment_charge_id']}\n\n"
                    response_text += f"Ваша подписка активирована. Теперь вам доступны расширенные функции DrillFlow."
                else:
                    response_text = f"✅ Платеж успешно выполнен!\n\n"
                    response_text += f"Сумма: {payment_amount} {payment_currency}\n"
                    response_text += f"Идентификатор платежа: {payment_info['telegram_payment_charge_id']}\n\n"
                    response_text += f"Спасибо за оплату! Ваш заказ принят в обработку."
                
                # Отправляем сообщение
                send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": response_text,
                    "parse_mode": "HTML"
                }
                
                req = urllib.request.Request(
                    send_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    print(f"Payment confirmation sent: {result}")
                
        except Exception as e:
            print(f"Error processing update: {e}")
            print(traceback.format_exc())
    
    def answer_callback_query(self, token, callback_query_id):
        """Отвечаем на callback query"""
        answer_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
        answer_data = {
            "callback_query_id": callback_query_id
        }
        
        req = urllib.request.Request(
            answer_url,
            data=json.dumps(answer_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Callback answered: {result}")
    
    def show_payment_options(self, token, chat_id):
        """Показываем выбор платежной системы"""
        message_text = "Выберите платежную систему для тестовой оплаты:"
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "PayMaster Test", "callback_data": "payment_paymaster"}
                ],
                [
                    {"text": "Redsys Test", "callback_data": "payment_redsys"}
                ]
            ]
        }
        
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message_text,
            "reply_markup": keyboard
        }
        
        req = urllib.request.Request(
            send_url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Payment options sent: {result}")
    
    def show_subscription_options(self, token, chat_id, user_id, user_name):
        """Показываем опции подписки"""
        message_text = "💳 Оформление подписки на DrillFlow\n\n"
        message_text += "С подпиской вы получите:\n"
        message_text += "✅ Доступ к расширенным функциям\n"
        message_text += "✅ Неограниченное количество заказов\n"
        message_text += "✅ Приоритетную поддержку\n\n"
        message_text += "Стоимость: 499 руб./месяц\n\n"
        message_text += "Выберите способ оплаты:"
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "Подписка через PayMaster", "callback_data": "subscribe_paymaster"}
                ],
                [
                    {"text": "Подписка через Redsys", "callback_data": "subscribe_redsys"}
                ]
            ]
        }
        
        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message_text,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        }
        
        req = urllib.request.Request(
            send_url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Subscription options sent: {result}")
    
    def send_invoice(self, token, chat_id, provider="paymaster", is_subscription=False):
        """Отправляем счет на оплату"""
        # Сгенерируем уникальный идентификатор для платежа
        payment_id = str(uuid.uuid4())
        
        # Создаем счет
        invoice_url = f"https://api.telegram.org/bot{token}/sendInvoice"
        
        # Выберем платежный провайдер в зависимости от параметра
        if provider == "redsys":
            # Redsys Test
            provider_token = "2051251535:TEST:OTk5MDA4ODgxLTAwNQ"
            provider_name = "Redsys"
        else:
            # PayMaster Test (по умолчанию)
            provider_token = "1744374395:TEST:115e73e15f41dc0a68e0"
            provider_name = "PayMaster"
        
        # Настройки в зависимости от типа платежа
        if is_subscription:
            title = f"Подписка DrillFlow ({provider_name})"
            description = f"Ежемесячная подписка на расширенные функции DrillFlow через {provider_name}. Автопродление каждые 30 дней."
            amount = 49900  # 499 рублей в копейках
            payload = f"subscription_{provider}_{payment_id}"
        else:
            title = f"Тестовая оплата DrillFlow ({provider_name})"
            description = f"Тестовая оплата услуг бурения через {provider_name}. Это демонстрационный платеж для проверки функциональности."
            amount = 50000  # 500 рублей в копейках
            payload = f"test_payment_{provider}_{payment_id}"
            
        prices = [
            {
                "label": "Услуги DrillFlow",
                "amount": amount
            }
        ]
        
        invoice_data = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "currency": "RUB",
            "prices": prices,
            "max_tip_amount": 10000,  # Максимальные чаевые - 100 рублей
            "suggested_tip_amounts": [5000, 10000],  # Предложенные чаевые - 50 и 100 рублей
            "start_parameter": f"payment_{provider}_{payment_id}",
            "need_name": True,  # Запрашиваем имя пользователя
            "need_phone_number": True,  # Запрашиваем номер телефона
            "need_email": True,  # Запрашиваем email
            "need_shipping_address": False,  # Не запрашиваем адрес доставки
            "is_flexible": False  # Фиксированная цена
        }
        
        req = urllib.request.Request(
            invoice_url,
            data=json.dumps(invoice_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print(f"Invoice sent via {provider_name}: {result}")
        except Exception as e:
            print(f"Error sending invoice via {provider_name}: {e}")
            print(traceback.format_exc())
            
            # Отправляем сообщение об ошибке
            error_message = f"Ошибка при создании счета через {provider_name}: {str(e)}"
            send_url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": error_message
            }
            
            req = urllib.request.Request(
                send_url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print(f"Error message sent: {result}") 