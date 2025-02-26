"""
Application configuration settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    # Project info
    PROJECT_NAME: str = "DrillFlow"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Bot settings
    TELEGRAM_TOKEN: str
    USE_POLLING: bool = False
    TELEGRAM_BOT_DOMAIN: str = ""
    BOT_WEBHOOK_URL: str = ""
    
    # Database settings
    DATABASE_URL: str
    POSTGRES_POOL_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 30
    POSTGRES_POOL_TIMEOUT: int = 30
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 100
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    
    # Security settings
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    YANDEX_API_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    
    # CORS settings
    CORS_ORIGINS: str = "*"
    
    # Vercel settings
    VERCEL: bool = False
    VERCEL_URL: Optional[str] = None
    
    # Application settings
    ENVIRONMENT: str = "development"
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
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "drillflow"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # Кэширование
    CACHE_TTL: int = 300
    CACHE_PREFIX: str = "drillflow"
    
    # Безопасность
    SSL_ENABLED: bool = True
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_SECOND: int = 100
    
    # Telegram
    BOT_WEBHOOK_DOMAIN: Optional[str] = None
    BOT_ADMIN_GROUP_ID: Optional[int] = None
    BOT_SUPPORT_GROUP_ID: Optional[int] = None
    
    # API ключи
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
    def get_database_url(self) -> str:
        """Получение URL базы данных"""
        if self.TESTING:
            return "sqlite:///./test.db"
        
        # Если указаны параметры PostgreSQL, формируем URL
        if self.POSTGRES_SERVER and self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_DB:
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        
        return self.DATABASE_URL
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()

settings = get_settings()

# Export all
__all__ = ["settings"] 