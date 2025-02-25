"""
Инициализация FastAPI приложения
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
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

    # Настройка шаблонов
    templates = Jinja2Templates(directory="app/templates")

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Добавляем обработчики исключений на уровне приложения
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Обработчик HTTP-исключений"""
        logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
        
        # Проверяем, запрос к API или к веб-интерфейсу
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        else:
            # Для веб-интерфейса перенаправляем на страницу ошибки
            return templates.TemplateResponse(
                "error.html", 
                {
                    "request": request,
                    "error_code": exc.status_code,
                    "error_message": exc.detail
                },
                status_code=exc.status_code
            )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Обработчик ошибок валидации"""
        error_detail = str(exc)
        logger.error(f"Validation error: {error_detail}")
        
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=422,
                content={"detail": "Ошибка валидации данных", "errors": exc.errors()}
            )
        else:
            return templates.TemplateResponse(
                "error.html", 
                {
                    "request": request,
                    "error_code": 422,
                    "error_message": "Ошибка в переданных данных"
                },
                status_code=422
            )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Обработчик общих исключений"""
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(traceback.format_exc())
        
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=500,
                content={"detail": "Внутренняя ошибка сервера"}
            )
        else:
            return templates.TemplateResponse(
                "error.html", 
                {
                    "request": request,
                    "error_code": 500,
                    "error_message": "Внутренняя ошибка сервера"
                },
                status_code=500
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

    return app 