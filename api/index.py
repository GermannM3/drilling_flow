"""
Точка входа для Vercel Serverless Functions.
"""
import os
import json

# Устанавливаем флаг, что мы в среде Vercel
os.environ['VERCEL'] = 'True'

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.application import create_app

# Создаем экземпляр приложения
app = create_app()

# Функция-обработчик для Vercel
def handler(request, context):
    """
    Функция-обработчик для Vercel Serverless Functions
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "API работает. Используйте FastAPI эндпоинты.",
            "version": app.version
        })
    } 