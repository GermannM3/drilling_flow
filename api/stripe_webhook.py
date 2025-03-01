"""
Обработчик webhook-уведомлений от Stripe.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import stripe
from api.stripe_subscription import handle_webhook_event  # Импортируем функцию обработки событий

# Инициализируем Stripe API
stripe_api_key = os.getenv("STRIPE_API_KEY", "")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Обработка GET-запросов. Возвращает статус сервиса.
        """
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "status": "webhook endpoint is working",
            "webhook_type": "stripe"
        }
        
        self.wfile.write(json.dumps(response_data).encode())
    
    def do_POST(self):
        """
        Обработка POST-запросов. Принимает уведомления от Stripe.
        """
        # Получаем данные запроса
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Получаем сигнатуру Stripe
        signature = self.headers.get('Stripe-Signature', '')
        
        # Обрабатываем событие
        try:
            result = handle_webhook_event(post_data, signature)
            
            if result:
                # Отправляем успешный ответ
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write('OK'.encode())
            else:
                # Отправляем ошибку
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write('Invalid webhook event'.encode())
        except Exception as e:
            # Отправляем ошибку
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error processing webhook: {str(e)}'.encode()) 