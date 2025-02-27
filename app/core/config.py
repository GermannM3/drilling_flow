"""
Конфигурация приложения
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки приложения
    PROJECT_NAME: str = "DrillFlow"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Платформа автоматизации распределения заказов на буровые работы"
    DEBUG: bool = False
    
    # Настройки Telegram
    TELEGRAM_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_BOT_DOMAIN: Optional[str] = None
    
    # Настройки Vercel
    VERCEL: bool = False
    USE_POLLING: bool = True
    
    # Настройки приложения
    ENVIRONMENT: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="",
        extra="ignore"
    )

settings = Settings()

# Export all
__all__ = ["settings"] 