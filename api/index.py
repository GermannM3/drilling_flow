"""
Точка входа для Vercel Serverless Functions.
"""
import os
from http.server import BaseHTTPRequestHandler

# Устанавливаем флаг, что мы в среде Vercel
os.environ['VERCEL'] = 'True'

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.application import create_app

# Создаем экземпляр приложения
app = create_app()

# Создаем класс-обработчик для Vercel
class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_content = {
            "message": "API работает. Используйте FastAPI эндпоинты."
        }
        
        self.wfile.write(bytes(str(response_content), "utf8"))
        return 