"""
Схемы данных для пользователей
"""
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    CONTRACTOR = "contractor"
    CLIENT = "client"

class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    
class UserCreate(UserBase):
    role: UserRoleEnum = UserRoleEnum.CLIENT
    
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
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

class ContractorProfileUpdate(BaseModel):
    work_radius: Optional[float] = Field(default=None, ge=0, le=100)
    service_types: Optional[List[str]] = None
    daily_capacity: Optional[int] = Field(default=None, ge=1, le=10)

class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    rating: float = 0.0
    is_active: bool
    is_verified: bool = False
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class ContractorResponse(UserResponse):
    work_radius: Optional[float] = None
    daily_capacity: Optional[int] = None
    service_types: List[str] = []
    
    class Config:
        orm_mode = True 