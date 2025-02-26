"""
Схемы для пользователей и клиентов
"""
from typing import Optional, List
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from enum import Enum
from .order import Order
from .base import BaseSchema, UserRoleEnum

class UserBase(BaseModel):
    telegram_id: str
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(BaseSchema):
    """Schema for creating a new user"""
    telegram_id: str
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str
    email: Optional[EmailStr] = None
    role: UserRoleEnum = UserRoleEnum.CLIENT

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    
    @validator('location_lat')
    def validate_lat(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Широта должна быть между -90 и 90')
        return v
        
    @validator('location_lon')
    def validate_lon(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Долгота должна быть между -180 и 180')
        return v

class User(UserCreate):
    """Schema for user with additional fields"""
    id: int
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    location_lat: Optional[float] = Field(None, ge=-90, le=90)
    location_lon: Optional[float] = Field(None, ge=-180, le=180)

    class Config:
        orm_mode = True

class ClientBase(BaseModel):
    name: str = Field(..., description="Имя клиента")
    contact: str = Field(..., description="Контактная информация")
    address: str = Field(..., description="Адрес")

class ClientCreate(ClientBase):
    user_id: int = Field(..., description="ID пользователя")

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None

class Client(ClientBase):
    id: int
    orders: List[Order] = []
    user_id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None 