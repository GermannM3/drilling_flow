"""
Схемы данных для заказов
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ServiceTypeEnum(str, Enum):
    DRILLING = "drilling"
    SEWAGE = "sewage"
    REPAIR = "repair"

class OrderStatusEnum(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderBase(BaseModel):
    title: str
    description: str
    location: str
    price: float = Field(ge=0)
    service_type: ServiceTypeEnum

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    status: Optional[OrderStatusEnum] = None

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
    status: OrderStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer_id: int
    contractor_id: Optional[int] = None
    ratings: List[OrderRatingResponse] = []
    
    class Config:
        orm_mode = True 