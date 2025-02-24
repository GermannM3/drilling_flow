"""
Модель рейтинга заказа
"""
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class OrderRating(Base):
    """Модель рейтинга заказа"""
    __tablename__ = "order_ratings"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    contractor_id = Column(Integer, ForeignKey("users.id"))
    client_rating = Column(Float)
    contractor_rating = Column(Float)
    rating = Column(Float)
    
    # Связи
    order = relationship("Order", back_populates="rating")
    contractor = relationship("User", back_populates="contractor_ratings") 