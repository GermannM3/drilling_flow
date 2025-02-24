"""
Модели базы данных
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

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
    first_name = Column(String)
    role = Column(String, default=UserRole.CLIENT)
    rating = Column(Float, default=0.0)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    orders = relationship("Order", back_populates="client", foreign_keys="Order.client_id")
    contractor_orders = relationship("Order", back_populates="contractor", foreign_keys="Order.contractor_id")
    contractor_ratings = relationship("OrderRating", back_populates="contractor")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    contractor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    service_type = Column(String)
    description = Column(String)
    address = Column(String)
    status = Column(String, default=OrderStatus.NEW)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    rating = Column(Float, nullable=True)
    
    client = relationship("User", back_populates="orders", foreign_keys=[client_id])
    contractor = relationship("User", back_populates="contractor_orders", foreign_keys=[contractor_id])
    ratings = relationship("OrderRating", back_populates="order")

# Экспортируем модели
__all__ = [
    "User", 
    "Order", 
    "ServiceType", 
    "UserRole", 
    "OrderStatus",
    "OrderRating"
]

# Импортируем OrderRating в конце, после определения всех зависимостей
from .order_rating import OrderRating 