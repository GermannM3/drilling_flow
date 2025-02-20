import requests

def calculate_distance(location1, location2):
    # Используем Google Maps API для расчета расстояния
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={location1}&destinations={location2}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data['rows'][0]['elements'][0]['distance']['value']  # расстояние в метрах 