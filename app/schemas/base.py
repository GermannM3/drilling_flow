"""
Base schemas and enums
"""
from datetime import datetime
from enum import Enum
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class BaseSchema(BaseModel):
    """Base schema with common configurations"""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )

class UserRoleEnum(str, Enum):
    """User role enum"""
    CLIENT = "client"
    CONTRACTOR = "contractor"
    ADMIN = "admin"

class ServiceTypeEnum(str, Enum):
    """Service type enum"""
    DRILLING = "drilling"
    SEWAGE = "sewage"
    REPAIR = "repair"

class OrderStatus(str, Enum):
    """Order status enum"""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

# Common field types
PositiveFloat = Annotated[float, Field(gt=0)]
Rating = Annotated[float, Field(ge=0, le=5)]
Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]
PhoneNumber = Annotated[str, Field(pattern=r'^\+?1?\d{9,15}$')]
Username = Annotated[str, Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')] 