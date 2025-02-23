"""
Импорты моделей
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from .order import Order
from .contractor import Contractor

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CONTRACTOR = "contractor"
    CLIENT = "client"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    username = Column(String)
    first_name = Column(String)
    role = Column(String, default=UserRole.CLIENT)
    rating = Column(Float, default=0.0)
    orders = relationship("Order", back_populates="client")
    contractor_orders = relationship("Order", back_populates="contractor")

class ServiceType(str, enum.Enum):
    DRILLING = "drilling"
    REPAIR = "repair"
    MAINTENANCE = "maintenance"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    contractor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    service_type = Column(String)
    description = Column(String)
    address = Column(String)
    status = Column(String, default="new")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    rating = Column(Float, nullable=True)
    
    client = relationship("User", back_populates="orders", foreign_keys=[client_id])
    contractor = relationship("User", back_populates="contractor_orders", foreign_keys=[contractor_id])

# Экспортируем модели
__all__ = ["User", "Order", "ServiceType", "UserRole"] 