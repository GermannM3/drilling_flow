"""
Конфигурация базы данных
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Для Vercel используем SQLite, для продакшена - PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./sql_app.db" if os.getenv("VERCEL") else 
    "postgresql+psycopg2://atributik:BpM3TIh2USFn0KBPj77qh9WerjTCqsad@dpg-cutmu00gph6c73b4gj20-a.oregon-postgres.render.com/drill_flow_db"
)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():
    """Получение сессии БД"""
    async with SessionLocal() as session:
        yield session

Base = declarative_base() 