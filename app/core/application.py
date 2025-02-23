"""
Инициализация FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .logger import setup_logging
from .config import get_settings
from app.routers import auth, orders, contractors, geo, webapp

# Настройка логирования
logger = setup_logging()
settings = get_settings()

def create_app() -> FastAPI:
    """
    Создает и настраивает экземпляр FastAPI
    Returns:
        FastAPI: Настроенное приложение
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключаем роуты
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(orders.router, prefix="/api", tags=["orders"])
    app.include_router(contractors.router, prefix="/api", tags=["contractors"])
    app.include_router(geo.router, prefix="/api", tags=["geo"])
    app.include_router(webapp.router, tags=["webapp"])

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up DrillFlow API")

    @app.get("/")
    async def root():
        return {
            "status": "ok",
            "version": settings.VERSION,
            "environment": "testing" if settings.TESTING else "production"
        }

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app 