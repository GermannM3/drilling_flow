import requests
from django.conf import settings

def calculate_distance(origin, destination):
    """
    Вычисляет расстояние между двумя точками через Google Maps Distance Matrix API.
    - origin: строка вида "lat,lng" исходной точки
    - destination: строка вида "lat,lng" точки назначения
    Возвращает расстояние в километрах или None в случае ошибки.
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?"
        f"origins={origin}&destinations={destination}&key={api_key}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        try:
            distance_meters = result['rows'][0]['elements'][0]['distance']['value']
            distance_km = distance_meters / 1000.0
            return distance_km
        except (IndexError, KeyError):
            return None
    return None 