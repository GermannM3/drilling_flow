from typing import Tuple, List
import aiohttp
from fastapi import HTTPException
from math import radians, sin, cos, sqrt, atan2
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.contractor import Contractor

class YandexGeoService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.geocode_url = "https://geocode-maps.yandex.ru/1.x/"
        self.router_url = "https://router.api.yandex.net/v2/route"
        
    async def get_coordinates(self, address: str) -> Tuple[float, float]:
        """Получение координат по адресу"""
        params = {
            "apikey": self.api_key,
            "geocode": address,
            "format": "json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.geocode_url, params=params) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Ошибка геокодирования")
                    
                data = await response.json()
                try:
                    pos = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
                    lon, lat = map(float, pos.split())
                    return lat, lon
                except (KeyError, IndexError):
                    raise HTTPException(status_code=404, detail="Адрес не найден")

    async def get_route(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> dict:
        """Построение маршрута между точками"""
        params = {
            "apikey": self.api_key,
            "waypoints": f"{origin[0]},{origin[1]}|{destination[0]},{destination[1]}",
            "mode": "driving"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.router_url, params=params) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Ошибка построения маршрута")
                    
                return await response.json()

def calculate_distance(coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
    """
    Вычисляет расстояние между двумя точками на сфере (формула гаверсинусов)
    Args:
        coords1: (lat1, lon1)
        coords2: (lat2, lon2)
    Returns:
        float: Расстояние в километрах
    """
    R = 6371  # Радиус Земли в км

    lat1, lon1 = map(radians, coords1)
    lat2, lon2 = map(radians, coords2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

async def find_nearest_contractors(
    location: Tuple[float, float],
    db: AsyncSession,
    max_distance: float = 50.0,
    required_rating: float = 4.0
) -> List[Contractor]:
    """
    Находит ближайших подрядчиков в заданном радиусе
    Args:
        location: (lat, lon) точка поиска
        max_distance: максимальное расстояние в км
        required_rating: минимальный рейтинг
    Returns:
        List[Contractor]: Список подходящих подрядчиков
    """
    # В реальном приложении здесь будет SQL запрос с PostGIS
    # Для примера используем простой фильтр
    contractors = await db.query(Contractor).filter(
        Contractor.rating >= required_rating
    ).all()

    return [
        c for c in contractors
        if calculate_distance(location, tuple(map(float, c.location.split(','))))
        <= max_distance
    ] 