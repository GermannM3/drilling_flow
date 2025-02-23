"""
Модель заказа
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..base import Base
import enum

class ServiceType(enum.Enum):
    DRILLING = "drilling"
    SEWAGE = "sewage"
    REPAIR = "repair"

class OrderStatus(enum.Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(Base):
    """Модель заказа на бурение"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=True)
    
    service_type = Column(Enum(ServiceType))
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(String)
    photo_url = Column(String, nullable=True)
    
    price = Column(Float, nullable=True)
    prepayment = Column(Float, nullable=True)
    payment_status = Column(String, default="pending")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Отношения
    client = relationship("User", back_populates="orders")
    contractor = relationship("Contractor", back_populates="orders")
    rating = relationship("OrderRating", back_populates="order", uselist=False) 