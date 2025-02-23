import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from app.core.application import create_app
from app.core.config import Settings, get_settings
from app.db.base import Base

def get_test_settings() -> Settings:
    """Настройки для тестов"""
    return Settings(
        TESTING=True,
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        POSTGRES_DB="test_db",
        POSTGRES_USER="test",
        POSTGRES_PASSWORD="test",
        POSTGRES_SERVER="localhost",
        TELEGRAM_TOKEN="test_token"
    )

# Создаем тестовое приложение
app = create_app()

# Переопределяем функцию получения настроек для тестов
app.dependency_overrides[get_settings] = get_test_settings

@pytest.fixture(scope="session")
def settings() -> Settings:
    """Фикстура настроек для тестов"""
    return get_test_settings()

@pytest.fixture(scope="session")
def client(settings) -> Generator:
    """Фикстура тестового клиента"""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
async def engine(settings):
    """Фикстура тестового движка БД"""
    if database_exists(settings.DATABASE_URL):
        drop_database(settings.DATABASE_URL)
    
    create_database(settings.DATABASE_URL)
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield engine
    finally:
        await engine.dispose()
        if database_exists(settings.DATABASE_URL):
            drop_database(settings.DATABASE_URL)

@pytest.fixture
async def db_session(engine) -> AsyncSession:
    """Фикстура сессии БД"""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close() 