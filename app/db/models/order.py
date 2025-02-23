"""
Модель заказа
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from ..base import Base

class Order(Base):
    """Модель заказа на бурение"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=True)
    status = Column(String, default="new")
    location = Column(String)
    description = Column(String)
    price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 