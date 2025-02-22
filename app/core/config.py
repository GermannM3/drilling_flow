from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "DrillFlow API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    REDIS_URL: str
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    TELEGRAM_TOKEN: str
    GOOGLE_MAPS_API_KEY: str
    
    ORIGINS: List[str] = ["*"]
    
    SECRET_KEY: str
    ENVIRONMENT: str = "prod"
    ALLOWED_HOSTS: List[str]
    CORS_ORIGINS: List[str]
    
    RATE_LIMIT_PER_MINUTE: int = 60
    
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings() 