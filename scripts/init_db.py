#!/usr/bin/env python
"""
Скрипт для инициализации базы данных
"""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from datetime import datetime

# Определяем модели
Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CONTRACTOR = "contractor"
    CLIENT = "client"

class OrderStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ServiceType(str, enum.Enum):
    DRILLING = "drilling"
    REPAIR = "repair"
    MAINTENANCE = "maintenance"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    username = Column(String)
    full_name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_contractor = Column(Boolean, default=False)
    
    # Для подрядчиков
    work_radius = Column(Float)  # в километрах
    max_orders_per_day = Column(Integer, default=2)
    current_orders = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String)
    location = Column(String)
    price = Column(Float)
    status = Column(String, default=OrderStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Внешние ключи
    customer_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    contractor_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

class OrderRating(Base):
    __tablename__ = "order_ratings"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(
        Integer, 
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    contractor_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    client_rating = Column(Float)
    contractor_rating = Column(Float)
    rating = Column(Float)

class Contractor(Base):
    __tablename__ = "contractors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    orders_completed = Column(Integer, default=0)
    location = Column(String, nullable=True)

def init_db():
    """
    Инициализация базы данных
    """
    # Получаем URL базы данных из переменной окружения
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://atributik:BpM3TIh2USFn0KBPj77qh9WerjTCqsad@dpg-cutmu00gph6c73b4gj20-a.oregon-postgres.render.com/drill_flow_db"
    )
    
    # Если URL содержит asyncpg, заменяем его на psycopg2
    if "asyncpg" in database_url:
        database_url = database_url.replace("asyncpg", "psycopg2")
    
    print(f"Connecting to database: {database_url}")
    
    # Создаем движок
    engine = create_engine(database_url)
    
    # Создаем таблицы
    Base.metadata.create_all(engine)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 