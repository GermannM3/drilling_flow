"""
Точка входа FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import get_settings
from app.routers import router as api_router
from app.core.init_db import init_db
from app.core.bot import setup_bot_commands

settings = get_settings()

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
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    # Монтируем директорию для медиафайлов
    media_path = Path(__file__).parent / "media"
    app.mount("/media", StaticFiles(directory=str(media_path)), name="media")

    # Подключаем метрики Prometheus
    Instrumentator().instrument(app).expose(app)

    # Подключаем роутеры
    app.include_router(api_router)

    @app.on_event("startup")
    async def startup_event():
        """Действия при запуске приложения"""
        # Инициализируем БД
        await init_db()
        # Устанавливаем команды бота
        await setup_bot_commands()

    @app.get("/health")
    async def health_check():
        """Проверка здоровья сервиса"""
        return {"status": "ok"}

    return app

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