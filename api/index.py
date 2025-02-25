"""
Точка входа для Vercel Serverless Functions.
"""
import os

# Устанавливаем флаг, что мы в среде Vercel
os.environ['VERCEL'] = 'True'

from fastapi import FastAPI
from app.core.application import create_app

# Создаем экземпляр приложения
app = create_app()

# Экспортируем ASGI приложение для Vercel
handler = app 