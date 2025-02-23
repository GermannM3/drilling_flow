"""
Конфигурация базы данных
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://atributik:BpM3TIh2USFn0KBPj77qh9WerjTCqsad@dpg-cutmu00gph6c73b4gj20-a.oregon-postgres.render.com/drill_flow_db"
)

# Создаем движок
engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Получение сессии БД"""
    async with AsyncSessionLocal() as session:
        yield session

Base = declarative_base() 