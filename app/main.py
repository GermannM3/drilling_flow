"""
Точка входа FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import configure_mappers
import asyncio
import os

from app.core.config import get_settings
from app.routers import router as api_router
from app.core.init_db import init_db
from app.core.bot import bot, dp, setup_bot_commands, start_polling
from app.db.models import User, Order, OrderRating  # Явно импортируем модели

settings = get_settings()

# Проверяем, находимся ли мы в среде Vercel (где файловая система только для чтения)
IS_VERCEL = os.environ.get('VERCEL', False)

def create_app() -> FastAPI:
    """Создание и настройка приложения"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Монтируем статические файлы
    static_path = Path(__file__).parent / "static"
    # Проверяем существование директории и создаем при необходимости, если не в среде Vercel
    if not IS_VERCEL:
        try:
            if not static_path.exists():
                static_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Не удалось создать директорию {static_path}: {e}")
    
    # Монтируем статические файлы с обработкой ошибок
    try:
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    except Exception as e:
        print(f"Ошибка при монтировании статических файлов: {e}")
        # В среде Vercel пропускаем монтирование, если директория не существует

    # Монтируем директорию для медиафайлов
    media_path = Path(__file__).parent / "media"
    # Проверяем существование директории и создаем при необходимости, если не в среде Vercel
    if not IS_VERCEL:
        try:
            if not media_path.exists():
                media_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Не удалось создать директорию {media_path}: {e}")
    
    # Монтируем медиа файлы с обработкой ошибок
    try:
        app.mount("/media", StaticFiles(directory=str(media_path)), name="media")
    except Exception as e:
        print(f"Ошибка при монтировании медиа файлов: {e}")
        # В среде Vercel пропускаем монтирование, если директория не существует

    # Подключаем метрики Prometheus
    Instrumentator().instrument(app).expose(app)

    # Подключаем роутеры
    app.include_router(api_router)

    @app.on_event("startup")
    async def startup_event():
        """Действия при запуске приложения"""
        await init_db()
        
        # Настраиваем и запускаем бота только если он не отключен
        if not settings.DISABLE_BOT:
            await setup_bot_commands()
            
            # Запускаем поллинг бота в фоновом режиме
            try:
                # Запускаем поллинг в фоновом режиме
                asyncio.create_task(start_polling())
                print("Bot polling started successfully")
            except Exception as e:
                print(f"Error starting bot polling: {e}")
        else:
            print("Bot is disabled in settings, skipping bot initialization")

    @app.get("/health")
    async def health_check():
        """Проверка здоровья сервиса"""
        return {"status": "ok"}

    return app

# Настраиваем маппинги SQLAlchemy
configure_mappers()

app = create_app()

@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "environment": "testing" if settings.TESTING else "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 