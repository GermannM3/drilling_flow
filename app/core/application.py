"""
Инициализация FastAPI приложения
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .logger import setup_logging
from .config import get_settings
from app.routers import auth, orders, contractors, geo, webapp
from pathlib import Path
import os
import traceback

# Настройка логирования
logger = setup_logging()
settings = get_settings()

# Проверяем, находимся ли мы в среде Vercel (где файловая система только для чтения)
IS_VERCEL = os.environ.get('VERCEL', False)

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

    # Проверяем и создаем директории для статических файлов только если не в среде Vercel
    if not IS_VERCEL:
        try:
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
        except OSError as e:
            logger.warning(f"Не удалось создать директории для статических файлов: {e}")
            logger.info("Работаем в режиме только для чтения, пропускаем создание директорий")

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
        
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Обработчик HTTP-исключений"""
        logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
        
        # Для API-запросов возвращаем JSON
        if request.url.path.startswith('/api'):
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail}
            )
        
        # Для веб-запросов перенаправляем на страницу ошибки
        return JSONResponse(
            status_code=307,  # Temporary Redirect
            headers={"Location": f"/error?code={exc.status_code}&message={exc.detail}"},
            content={"redirect": True}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Обработчик ошибок валидации запросов"""
        logger.error(f"Validation error: {str(exc)}")
        
        # Для API-запросов возвращаем JSON с деталями ошибок
        if request.url.path.startswith('/api'):
            return JSONResponse(
                status_code=422,
                content={"error": "Ошибка валидации данных", "details": exc.errors()}
            )
        
        # Для веб-запросов перенаправляем на страницу ошибки
        return JSONResponse(
            status_code=307,  # Temporary Redirect
            headers={"Location": "/error?code=422&message=Ошибка валидации данных"},
            content={"redirect": True}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Обработчик общих исключений"""
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # Для API-запросов возвращаем JSON
        if request.url.path.startswith('/api'):
            return JSONResponse(
                status_code=500,
                content={"error": "Внутренняя ошибка сервера"}
            )
        
        # Для веб-запросов перенаправляем на страницу ошибки
        return JSONResponse(
            status_code=307,  # Temporary Redirect
            headers={"Location": "/error?code=500&message=Внутренняя ошибка сервера"},
            content={"redirect": True}
        )

    return app 