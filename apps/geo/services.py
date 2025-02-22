import googlemaps
from django.conf import settings

class GeocodingService:
    def __init__(self):
        self.client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def geocode_address(self, address):
        """Получает координаты по адресу"""
        try:
            result = self.client.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': result[0]['formatted_address']
                }
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
        return None

    def reverse_geocode(self, lat, lng):
        """Получает адрес по координатам"""
        try:
            result = self.client.reverse_geocode((lat, lng))
            if result:
                return result[0]['formatted_address']
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
        return None 