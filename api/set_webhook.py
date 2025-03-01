from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Получаем токен и URL вебхука
        token = os.getenv("TELEGRAM_TOKEN", "")
        webhook_domain = os.getenv("BOT_WEBHOOK_DOMAIN", "drilling-flow.vercel.app")
        webhook_url = f"https://{webhook_domain}/webhook"
        
        response_data = {
            "status": "processing",
            "webhook_url": webhook_url
        }
        
        # Пытаемся установить вебхук
        try:
            # Сначала удаляем текущий вебхук
            delete_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
            with urllib.request.urlopen(delete_url) as response:
                delete_result = json.loads(response.read().decode())
                response_data["delete_result"] = delete_result
            
            # Затем устанавливаем новый вебхук
            set_url = f"https://api.telegram.org/bot{token}/setWebhook?url={urllib.parse.quote(webhook_url)}"
            with urllib.request.urlopen(set_url) as response:
                set_result = json.loads(response.read().decode())
                response_data["set_result"] = set_result
                
            # Получаем информацию о вебхуке
            info_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
            with urllib.request.urlopen(info_url) as response:
                webhook_info = json.loads(response.read().decode())
                response_data["webhook_info"] = webhook_info
                
            response_data["status"] = "success"
        except Exception as e:
            response_data["status"] = "error"
            response_data["error"] = str(e)
        
        self.wfile.write(json.dumps(response_data).encode()) 