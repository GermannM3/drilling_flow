"""
Модель пользователя
"""
from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship
from ..base import Base

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String, nullable=True)
    full_name = Column(String)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_contractor = Column(Boolean, default=False)
    
    # Для подрядчиков
    work_radius = Column(Float, nullable=True)  # в километрах
    max_orders_per_day = Column(Integer, default=2)
    current_orders = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    
    # Отношения
    orders = relationship("Order", back_populates="client")
    contractor_profile = relationship("Contractor", back_populates="user", uselist=False) 