"""
Модель подрядчика
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Contractor(Base):
    """Модель подрядчика"""
    __tablename__ = "contractors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    orders_completed = Column(Integer, default=0)
    location = Column(String, nullable=True)

# Импортируем после определения класса
from app.db.models.user import User

# Добавляем отношения после импорта
Contractor.user = relationship(
    User, 
    foreign_keys=[Contractor.user_id],
    backref="contractor_profile"
) 