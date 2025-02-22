from fastapi import APIRouter, Depends
from ..services.geo import GeoService
from ..schemas.geo import GeoLocation, Address

router = APIRouter()
geo_service = GeoService()

@router.get("/geocode")
async def geocode_address(address: str):
    return await geo_service.geocode_address(address)

@router.get("/nearby-contractors")
async def find_nearby_contractors(lat: float, lon: float, radius: int = 10):
    return await geo_service.find_nearby_contractors(lat, lon, radius) 