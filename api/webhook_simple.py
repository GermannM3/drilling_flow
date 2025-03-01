from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse
import traceback

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
                
                # Формируем ответ в зависимости от команды
                if text == "/start":
                    response_text = f"Привет, {user_name}!\n\nДобро пожаловать в DrillFlow - платформу для управления буровыми работами.\n\n🔹 Заказчики могут размещать заказы\n🔹 Подрядчики могут принимать заказы\n🔹 Автоматическое распределение заказов"
                    
                    # Создаем инлайн-клавиатуру
                    keyboard = {
                        "inline_keyboard": [
                            [
                                {"text": "📋 Профиль", "callback_data": "profile"},
                                {"text": "📦 Заказы", "callback_data": "orders"}
                            ],
                            [
                                {"text": "❓ Помощь", "callback_data": "help"},
                                {"text": "📊 Статистика", "callback_data": "stats"}
                            ]
                        ]
                    }
                    
                    # Отправляем сообщение с клавиатурой
                    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                    data = {
                        "chat_id": chat_id,
                        "text": response_text,
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
                        print(f"Message with keyboard sent: {result}")
                    
                    return
                    
                elif text == "/help":
                    response_text = "Список доступных команд:\n/start - начать работу с ботом\n/help - показать справку\n/profile - ваш профиль\n/orders - ваши заказы"
                elif text == "/profile":
                    response_text = f"Профиль пользователя {user_name}\nID: {update['message']['from']['id']}\nСтатус: Активен"
                elif text == "/orders":
                    response_text = "У вас пока нет активных заказов."
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
                
                # Формируем ответ в зависимости от данных колбэка
                if data == "profile":
                    response_text = f"Профиль пользователя {user_name}\nID: {update['callback_query']['from']['id']}\nСтатус: Активен"
                elif data == "orders":
                    response_text = "У вас пока нет активных заказов."
                elif data == "help":
                    response_text = "Раздел помощи. Здесь будет информация о том, как пользоваться ботом."
                elif data == "stats":
                    response_text = "Ваша статистика:\nЗаказов выполнено: 0\nРейтинг: ⭐⭐⭐⭐⭐"
                else:
                    response_text = f"Выбрано: {data}"
                
                # Отвечаем на колбэк
                answer_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                answer_data = {
                    "callback_query_id": callback_id
                }
                
                req = urllib.request.Request(
                    answer_url,
                    data=json.dumps(answer_data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    print(f"Callback answered: {result}")
                
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
                
        except Exception as e:
            print(f"Error processing update: {e}")
            print(traceback.format_exc()) 