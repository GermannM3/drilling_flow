"""
Точка входа для Vercel Serverless Functions.
"""

from app.core.application import create_app

app = create_app()

# Экспортируем приложение как handler для Vercel
handler = app 