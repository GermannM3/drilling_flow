"""
Модель рейтинга заказа
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, text
from sqlalchemy.orm import relationship
from app.db.base import Base

class OrderRating(Base):
    """Модель рейтинга заказа"""
    __tablename__ = "order_ratings"
    __table_args__ = {
        "extend_existing": True
    }

    id = Column(Integer, primary_key=True)
    order_id = Column(
        Integer, 
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    contractor_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    client_rating = Column(Float)
    contractor_rating = Column(Float)
    rating = Column(Float)

# Импортируем классы после определения OrderRating
from app.db.models.order import Order
from app.db.models.user import User

# Добавляем отношения после импорта классов
OrderRating.order = relationship(
    Order,
    back_populates="ratings",
    foreign_keys=[OrderRating.order_id]
)
OrderRating.contractor = relationship(
    User,
    back_populates="contractor_ratings",
    foreign_keys=[OrderRating.contractor_id]
) 