"""
Основной файл приложения FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.core.config import settings

def create_app() -> FastAPI:
    """
    Создание и настройка экземпляра FastAPI
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем роутеры
    app.include_router(api_router)

    @app.get("/")
    async def root():
        """
        Корневой эндпоинт для проверки работоспособности
        """
        return {
            "status": "ok",
            "message": "DrillFlow API работает",
            "version": settings.VERSION
        }

    return app 