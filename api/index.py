"""
Точка входа для Vercel Serverless Functions.
"""
import os

# Устанавливаем флаг, что мы в среде Vercel
os.environ['VERCEL'] = 'True'

from app.core.application import create_app

app = create_app()

# Экспортируем приложение как handler для Vercel
handler = app 