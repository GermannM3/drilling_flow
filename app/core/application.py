"""
Инициализация FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .logger import setup_logging
from .config import get_settings

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

    return app 