"""
Точка входа для Vercel Serverless Functions.
"""
import os
import json

# Устанавливаем флаг, что мы в среде Vercel
os.environ['VERCEL'] = 'True'

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
            "message": "API работает. Используйте FastAPI эндпоинты."
        })
    } 