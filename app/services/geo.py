from typing import Tuple, List
import aiohttp
from fastapi import HTTPException

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