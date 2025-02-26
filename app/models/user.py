"""
User models for SQLAlchemy
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Float, Boolean, DateTime, Integer,
    Enum as SQLEnum, ForeignKey, ARRAY
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.schemas.base import UserRoleEnum

class User(Base):
    """User model"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    role: Mapped[UserRoleEnum] = mapped_column(SQLEnum(UserRoleEnum))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    orders: Mapped[List["Order"]] = relationship(
        back_populates="client",
        foreign_keys="[Order.client_id]"
    )
    contractor_orders: Mapped[List["Order"]] = relationship(
        back_populates="contractor",
        foreign_keys="[Order.contractor_id]"
    )
    contractor_profile: Mapped[Optional["ContractorProfile"]] = relationship(
        back_populates="user",
        uselist=False
    )

class ContractorProfile(Base):
    """Contractor profile model"""
    __tablename__ = "contractor_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    
    company_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    specializations: Mapped[List[str]] = mapped_column(ARRAY(String))
    
    work_radius_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    completed_orders: Mapped[int] = mapped_column(Integer, default=0)
    failed_orders: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped[User] = relationship(back_populates="contractor_profile") 