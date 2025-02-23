import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import Settings

client = TestClient(app)

def test_health_check():
    """Тест endpoint проверки здоровья"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.parametrize("endpoint", [
    "/api/orders",
    "/api/contractors",
    "/api/profile"
])
def test_protected_endpoints_unauthorized(endpoint):
    """Тест защищенных endpoints без авторизации"""
    response = client.get(endpoint)
    assert response.status_code == 401

def test_invalid_token():
    """Тест невалидного токена"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/profile", headers=headers)
    assert response.status_code == 401

@pytest.mark.parametrize("coordinates", [
    {"lat": 55.7558, "lon": 37.6173},  # Москва
    {"lat": 59.9343, "lon": 30.3351},  # Санкт-Петербург
    {"lat": 0, "lon": 0},  # Нулевые координаты
])
def test_geo_validation(coordinates):
    """Тест валидации геокоординат"""
    response = client.post("/api/geo/validate", json=coordinates)
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data 