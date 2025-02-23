"""
Точка входа в приложение
"""
from .core.application import create_app
from .routers import orders, contractors, auth, geo, webapp
from .core.health_check import router as health_router
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.init_db import init_db

# Инициализируем БД при старте
init_db()

# Создаем приложение
app = create_app()

# Добавляем метрики Prometheus
Instrumentator().instrument(app).expose(app)

# Подключение роутеров
app.include_router(health_router)
app.include_router(auth)
app.include_router(orders)
app.include_router(contractors)
app.include_router(geo)
app.include_router(webapp)

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