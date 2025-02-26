"""
Утилиты для работы с геолокацией
"""
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Вычисляет расстояние между двумя точками на земной поверхности в километрах
    используя формулу гаверсинусов
    
    Args:
        lat1: Широта первой точки
        lon1: Долгота первой точки
        lat2: Широта второй точки
        lon2: Долгота второй точки
        
    Returns:
        float: Расстояние в километрах
    """
    # Радиус Земли в километрах
    R = 6371.0
    
    # Конвертируем координаты в радианы
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    
    # Разница координат
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Формула гаверсинусов
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Расстояние в километрах
    distance = R * c
    
    return distance

def format_location(lat: float, lon: float) -> str:
    """
    Форматирует координаты в читаемый вид
    
    Args:
        lat: Широта
        lon: Долгота
        
    Returns:
        str: Отформатированные координаты
    """
    return f"{lat:.6f}°, {lon:.6f}°" 