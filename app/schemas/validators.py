from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class OrderCreate(BaseModel):
    service_type: str = Field(..., regex="^(drilling|sewer|repair)$")
    address: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)

    @validator('service_type')
    def validate_service_type(cls, v):
        allowed = ['drilling', 'sewer', 'repair']
        if v not in allowed:
            raise ValueError(f'service_type must be one of {allowed}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "service_type": "drilling",
                "address": "ул. Примерная, д. 1",
                "description": "Бурение скважины на воду",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        } 