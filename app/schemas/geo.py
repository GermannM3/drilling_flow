"""
Схемы для геоданных
"""
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, validator

class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.lat, self.lon)

class GeocodeRequest(BaseModel):
    address: str

class GeocodeResponse(BaseModel):
    address: str
    coordinates: Coordinates

class RouteRequest(BaseModel):
    origin: Coordinates
    destination: Coordinates
    
class RoutePointInfo(BaseModel):
    address: str
    coordinates: Coordinates
    
class RouteInfo(BaseModel):
    distance: float  # в километрах
    duration: int    # в секундах
    
class RouteResponse(BaseModel):
    origin: RoutePointInfo
    destination: RoutePointInfo
    route: RouteInfo

class NearbyContractorsRequest(BaseModel):
    coordinates: Coordinates
    max_distance: Optional[float] = Field(50.0, ge=0, le=200)
    required_rating: Optional[float] = Field(4.0, ge=0, le=5)
    service_type: Optional[str] = None 