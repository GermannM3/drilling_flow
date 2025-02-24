"""
Конфигурация приложения
"""
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки приложения"""
    # Основные настройки
    PROJECT_NAME: str = "DrillFlow"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "ElderCade"
    DEBUG: bool = False
    
    # Настройки сервера
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
    DATABASE_URL: str
    POSTGRES_POOL_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 30
    POSTGRES_POOL_TIMEOUT: int = 30

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 100
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5

    # Кэширование
    CACHE_TTL: int = 300
    CACHE_PREFIX: str = "drillflow"

    # JWT
    JWT_SECRET_KEY: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_SECOND: int = 100

    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_PATH: str = "/app/logs"

    # API Keys
    YANDEX_API_KEY: str = "your-yandex-api-key"
    TELEGRAM_TOKEN: str
    BOT_WEBHOOK_DOMAIN: str
    BOT_WEBHOOK_URL: Optional[str] = None
    BOT_ADMIN_GROUP_ID: Optional[int] = None
    BOT_SUPPORT_GROUP_ID: Optional[int] = None

    # CORS
    ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = ["*"]

    # Тестирование
    TESTING: bool = False
    ENV: str = "production"

    @property
    def get_database_url(self) -> str:
        """Формирует URL для подключения к базе данных"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
            
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Возвращает объект настроек приложения
    Returns:
        Settings: Объект с настройками
    """
    return Settings()

settings = get_settings() 