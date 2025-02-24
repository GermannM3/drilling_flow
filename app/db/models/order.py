"""
Модель заказа
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class ServiceType(enum.Enum):
    DRILLING = "drilling"
    SEWAGE = "sewage"
    REPAIR = "repair"

class OrderStatus(str, enum.Enum):
    """Статусы заказа"""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(Base):
    """Модель заказа"""
    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    location = Column(String)
    price = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Внешние ключи
    customer_id = Column(Integer, ForeignKey("users.id"))
    contractor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Связи
    customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_orders")
    contractor = relationship("User", foreign_keys=[contractor_id], back_populates="contractor_orders")
    ratings = relationship("OrderRating", back_populates="order") 