"""
Base schemas and enums
"""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """Base schema with common configurations"""
    model_config = ConfigDict(from_attributes=True)

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