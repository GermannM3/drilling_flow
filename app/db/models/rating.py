"""
Модель рейтинга заказа
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..base import Base

class OrderRating(Base):
    __tablename__ = "order_ratings"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    rating = Column(Float, nullable=False)  # от 1 до 5
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="rating") 