"""
Модель заказа
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, text
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
    __table_args__ = {
        "extend_existing": True
    }

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    location = Column(String)
    price = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW)
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

# Импортируем классы после определения Order
from app.db.models.user import User
from app.db.models.rating import OrderRating

# Добавляем отношения после импорта классов
Order.customer = relationship(
    User,
    foreign_keys=[Order.customer_id],
    back_populates="customer_orders"
)
Order.contractor = relationship(
    User,
    foreign_keys=[Order.contractor_id],
    back_populates="contractor_orders"
)
Order.ratings = relationship(
    OrderRating,
    back_populates="order",
    cascade="all, delete-orphan"
) 