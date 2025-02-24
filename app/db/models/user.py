"""
Модель пользователя
"""
from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True)
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
    
    # Связи
    customer_orders = relationship("Order", foreign_keys="Order.customer_id", back_populates="customer")
    contractor_orders = relationship("Order", foreign_keys="Order.contractor_id", back_populates="contractor")
    contractor_ratings = relationship("OrderRating", back_populates="contractor") 