"""
Конфигурация базы данных
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

def get_database_url() -> str:
    """Получение URL базы данных в зависимости от окружения"""
    if os.getenv("VERCEL"):
        return "sqlite:///./sql_app.db"
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://atributik:BpM3TIh2USFn0KBPj77qh9WerjTCqsad@dpg-cutmu00gph6c73b4gj20-a.oregon-postgres.render.com/drill_flow_db"
    )

DATABASE_URL = get_database_url()
Base = declarative_base()

if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    async def get_db():
        """Получение сессии БД для SQLite"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
else:
    # Создаем асинхронный движок
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True
    )

    # Создаем фабрику асинхронных сессий
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Функция для получения сессии БД
    async def get_db():
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close() 