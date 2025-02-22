from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Базовые настройки
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "atributik"
    POSTGRES_PASSWORD: str = "1213276"
    POSTGRES_DB: str = "drillflow_db"
    
    # API ключи
    TELEGRAM_TOKEN: str = "7554540052:AAEvde_xL9d85kbJBdxPu8B6Mo4UEMF-qBs"
    YANDEX_API_KEY: str = "fa6c1c44-4070-4d63-819b-bd6fbb5bae9e"
    
    # Безопасность
    JWT_SECRET_KEY: str = "ElderCade"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Сервер
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # Опциональные настройки
    GOOGLE_MAPS_API_KEY: str = ""
    SECRET_KEY: str = "default-secret-key"
    ALLOWED_HOSTS: list = ["*"]
    CORS_ORIGINS: list = ["*"]

settings = Settings() 