"""
Конфигурация приложения
"""
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    PROJECT_NAME: str = "DrillFlow"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    TESTING: bool = False
    
    # Python
    PYTHON_VERSION: str = "3.11"
    PYTHONUNBUFFERED: str = "1"
    PYTHONDONTWRITEBYTECODE: str = "1"
    PYTHONOPTIMIZE: str = "2"
    
    # Сервер
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4
    BACKLOG: int = 2048
    MAX_REQUESTS: int = 10000
    KEEPALIVE: int = 120
    
    # База данных
    DATABASE_URL: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "drillflow"
    POSTGRES_POOL_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 30
    POSTGRES_POOL_TIMEOUT: int = 30
    
    @property
    def get_database_url(self) -> str:
        """Получение URL базы данных"""
        if self.TESTING:
            return "sqlite+aiosqlite:///./test.db"
        return self.DATABASE_URL
    
    # Redis
    REDIS_URL: str
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_MAX_CONNECTIONS: int = 100
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    
    # Кэширование
    CACHE_TTL: int = 300
    CACHE_PREFIX: str = "drillflow"
    
    # Безопасность
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SSL_ENABLED: bool = True
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_SECOND: int = 100
    
    # Telegram
    TELEGRAM_TOKEN: str
    BOT_WEBHOOK_URL: Optional[str] = None
    BOT_WEBHOOK_DOMAIN: Optional[str] = None
    BOT_ADMIN_GROUP_ID: Optional[int] = None
    BOT_SUPPORT_GROUP_ID: Optional[int] = None
    TELEGRAM_BOT_DOMAIN: str = "https://drilling-flow.vercel.app"
    
    # CORS и хосты
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    CORS_ORIGINS: str = "*"
    
    # API ключи
    YANDEX_API_KEY: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_PATH: str = "/app/logs"

    # Медиафайлы
    MEDIA_ROOT: str = "app/media"
    MEDIA_URL: str = "/media"
    MAX_UPLOAD_SIZE: int = 5_242_880  # 5MB в байтах
    ALLOWED_MEDIA_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf"
    ]

    @property
    def allowed_hosts_list(self) -> List[str]:
        """Преобразует строку ALLOWED_HOSTS в список"""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        """Преобразует строку CORS_ORIGINS в список"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    """Получение настроек приложения"""
    return Settings()

settings = get_settings() 