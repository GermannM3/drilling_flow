"""
Тесты API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.config import get_settings

def test_health_check(client):
    """Тест endpoint проверки здоровья"""
    response = client.get("/health")
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert "version" in data

@pytest.mark.parametrize("endpoint", [
    "/api/orders",
    "/api/contractors",
    "/api/profile"
])
def test_protected_endpoints_unauthorized(client, endpoint):
    """Тест защищенных endpoints без авторизации"""
    response = client.get(endpoint)
    assert response.status_code in [401, 403]  # Unauthorized или Forbidden

def test_invalid_token(client):
    """Тест невалидного токена"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/profile", headers=headers)
    assert response.status_code in [401, 403]

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