"""
Схемы для заказов и подрядчиков
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from .base import BaseSchema, ServiceTypeEnum, OrderStatus, PositiveFloat, Rating

class OrderBase(BaseModel):
    title: str
    description: str
    location: str
    price: float = Field(ge=0)
    service_type: ServiceTypeEnum

class OrderCreate(BaseSchema):
    """Schema for creating a new order"""
    client_id: str
    service_type: ServiceTypeEnum
    address: str
    description: str = Field(min_length=10, max_length=1000)
    status: OrderStatus = OrderStatus.NEW
    price: Optional[PositiveFloat] = None

class OrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    status: Optional[OrderStatus] = None

class OrderRatingBase(BaseModel):
    rating: float = Field(ge=1, le=5)
    comment: Optional[str] = None

class OrderRatingCreate(OrderRatingBase):
    order_id: int

class OrderRatingResponse(OrderRatingBase):
    id: int
    order_id: int
    contractor_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class OrderResponse(OrderBase):
    id: int
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer_id: int
    contractor_id: Optional[int] = None
    ratings: List[OrderRatingResponse] = []
    
    class Config:
        orm_mode = True

class ContractorBase(BaseModel):
    name: str = Field(..., description="Имя подрядчика")
    contact: str = Field(..., description="Контактная информация")
    specialization: str = Field(..., description="Специализация")
    work_radius: int = Field(..., gt=0, description="Радиус работы (км)")
    max_load: int = Field(..., gt=0, description="Максимальная загрузка")

class ContractorCreate(ContractorBase):
    pass

class ContractorUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    specialization: Optional[str] = None
    work_radius: Optional[int] = Field(None, gt=0)
    max_load: Optional[int] = Field(None, gt=0)

class Contractor(ContractorBase):
    id: int
    rating: float = Field(0.0, ge=0, le=5, description="Рейтинг подрядчика")
    orders_completed: int = Field(0, ge=0, description="Количество выполненных заказов")
    orders_failed: int = Field(0, ge=0, description="Количество проваленных заказов")

    class Config:
        orm_mode = True

class Order(OrderCreate):
    """Schema for order with additional fields"""
    id: int
    contractor_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    rating: Optional[Rating] = None

class OrderRating(BaseSchema):
    """Schema for order rating"""
    order_id: int
    rating: Rating
    comment: Optional[str] = Field(None, min_length=10, max_length=500)
    created_at: datetime

class ContractorOrder(Order):
    """Schema for order with contractor details"""
    client_name: str
    client_phone: Optional[str] = None
    distance_km: Optional[PositiveFloat] = None 