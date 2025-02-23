"""
Модель подрядчика
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class Contractor(Base):
    """Модель подрядчика"""
    __tablename__ = "contractors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    rating = Column(Float, default=0.0)
    orders_completed = Column(Integer, default=0)
    location = Column(String, nullable=True)

    # Определяем отношения без обратных ссылок
    contractor_orders = relationship("Order", back_populates="contractor", foreign_keys="Order.contractor_id") 