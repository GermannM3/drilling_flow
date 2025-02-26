"""
Order models for SQLAlchemy
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.schemas.base import ServiceTypeEnum, OrderStatus

class Order(Base):
    """Order model"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[str] = mapped_column(String, index=True)
    contractor_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    
    service_type: Mapped[ServiceTypeEnum] = mapped_column(SQLEnum(ServiceTypeEnum))
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.NEW)
    
    address: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(String(1000))
    
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
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
    ratings: Mapped[list["OrderRating"]] = relationship(back_populates="order")
    client: Mapped["User"] = relationship(
        back_populates="orders",
        foreign_keys=[client_id]
    )
    contractor: Mapped[Optional["User"]] = relationship(
        back_populates="contractor_orders",
        foreign_keys=[contractor_id]
    )

class OrderRating(Base):
    """Order rating model"""
    __tablename__ = "order_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    rating: Mapped[float] = mapped_column(Float)
    comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    order: Mapped[Order] = relationship(back_populates="ratings") 