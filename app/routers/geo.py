from fastapi import APIRouter, Depends
from ..services.geo import YandexGeoService
from ..core.config import get_settings, Settings
from typing import Dict

router = APIRouter(prefix="/api/geo", tags=["geo"])

@router.get("/geocode/{address}")
async def geocode_address(address: str, geo_service: YandexGeoService = Depends(lambda: YandexGeoService(get_settings().YANDEX_API_KEY))):
    return await geo_service.get_coordinates(address)

@router.get("/route")
async def get_route(
    origin_address: str, 
    destination_address: str,
    geo_service: YandexGeoService = Depends(lambda: YandexGeoService(get_settings().YANDEX_API_KEY))
):
    origin_coords = await geo_service.get_coordinates(origin_address)
    dest_coords = await geo_service.get_coordinates(destination_address)
    return await geo_service.get_route(origin_coords, dest_coords)

@router.post("/validate")
async def validate_coordinates(
    coordinates: Dict[str, float],
    settings: Settings = Depends(get_settings)
) -> Dict[str, bool]:
    """Валидация координат"""
    try:
        lat = coordinates.get("lat", 0)
        lon = coordinates.get("lon", 0)
        # Проверка валидности координат
        valid = -90 <= lat <= 90 and -180 <= lon <= 180
        return {"valid": valid}
    except Exception:
        return {"valid": False} 