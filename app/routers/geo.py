from fastapi import APIRouter, Depends
from ..services.geo import YandexGeoService
from ..core.config import get_settings

router = APIRouter(prefix="/geo", tags=["geo"])
settings = get_settings()

@router.get("/geocode/{address}")
async def geocode_address(address: str, geo_service: YandexGeoService = Depends(lambda: YandexGeoService(settings.YANDEX_API_KEY))):
    return await geo_service.get_coordinates(address)

@router.get("/route")
async def get_route(
    origin_address: str, 
    destination_address: str,
    geo_service: YandexGeoService = Depends(lambda: YandexGeoService(settings.YANDEX_API_KEY))
):
    origin_coords = await geo_service.get_coordinates(origin_address)
    dest_coords = await geo_service.get_coordinates(destination_address)
    return await geo_service.get_route(origin_coords, dest_coords) 