"""
Инициализация FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .logger import setup_logging
from .config import get_settings
from app.routers import auth, orders, contractors, geo, webapp
from pathlib import Path

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
        description="API для сервиса бурения скважин"
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Проверяем и создаем директории для статических файлов
    base_dir = Path(__file__).resolve().parent.parent
    
    # Директория для статических файлов
    static_dir = base_dir / "static"
    if not static_dir.exists():
        static_dir.mkdir(parents=True, exist_ok=True)
        
    # Директория для статических файлов веб-приложения
    webapp_static_dir = static_dir / "webapp"
    if not webapp_static_dir.exists():
        webapp_static_dir.mkdir(parents=True, exist_ok=True)
        (webapp_static_dir / ".gitkeep").touch()
    
    # Директория для шаблонов
    templates_dir = base_dir / "templates"
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)

    # Подключаем роуты
    app.include_router(auth, prefix="/api", tags=["auth"])
    app.include_router(orders, prefix="/api", tags=["orders"])
    app.include_router(contractors, prefix="/api", tags=["contractors"])
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