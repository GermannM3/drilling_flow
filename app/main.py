"""
Точка входа в приложение
"""
from .core.application import create_app
from .routers import orders, contractors, auth, geo, webapp
from .core.health_check import router as health_router
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.init_db import init_db
from .core.bot import setup_bot_commands
import asyncio
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Инициализируем БД при старте
init_db()

# Создаем приложение
app = create_app()

# Монтируем статические файлы
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent / "static")),
    name="static"
)

# Добавляем метрики Prometheus
Instrumentator().instrument(app).expose(app)

# Подключение роутеров
app.include_router(health_router)
app.include_router(auth)
app.include_router(orders)
app.include_router(contractors)
app.include_router(geo)
app.include_router(webapp.router)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "environment": "testing" if settings.TESTING else "production"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    # Устанавливаем команды бота
    await setup_bot_commands()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 