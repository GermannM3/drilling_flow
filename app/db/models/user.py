"""
Модель пользователя
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..base import Base

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    orders = relationship("Order", back_populates="client")
    contractor_profile = relationship("Contractor", back_populates="user", uselist=False) 