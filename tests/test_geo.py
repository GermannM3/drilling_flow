import pytest
from app.services.geo import calculate_distance, find_nearest_contractors

@pytest.mark.parametrize("coords1,coords2,expected", [
    ((55.7558, 37.6173), (55.7558, 37.6173), 0),  # Одинаковые координаты
    ((55.7558, 37.6173), (59.9343, 30.3351), 634),  # Москва - Питер
])
def test_distance_calculation(coords1, coords2, expected):
    """Тест расчета расстояния между точками"""
    distance = calculate_distance(coords1, coords2)
    assert abs(distance - expected) <= 1  # Погрешность 1 км

@pytest.mark.asyncio
async def test_find_contractors():
    """Тест поиска ближайших подрядчиков"""
    order_location = (55.7558, 37.6173)  # Москва
    contractors = await find_nearest_contractors(
        order_location,
        max_distance=100,
        required_rating=4.0
    )
    assert isinstance(contractors, list)
    if contractors:
        assert all(c.rating >= 4.0 for c in contractors) 