import pytest
from app.services.order_distribution import distribute_order
from app.services.rating import calculate_contractor_rating
from app.db.models import Order, User, Contractor, ServiceType

@pytest.mark.asyncio
async def test_order_distribution(db_session):
    """Тест распределения заказов"""
    # Создаем тестовых подрядчиков
    contractors = []
    for i, data in enumerate([
        (4.5, 50), (3.8, 30), (4.9, 100)
    ]):
        rating, radius = data
        user = User(
            telegram_id=1000+i,
            full_name=f"Contractor {i}",
            is_contractor=True,
            work_radius=radius,
            rating=rating
        )
        contractor = Contractor(
            user=user,
            latitude=55.7558,
            longitude=37.6173
        )
        contractors.append(contractor)
        db_session.add(user)
        db_session.add(contractor)
    
    await db_session.commit()
    
    # Создаем заказ
    order = Order(
        latitude=55.7558,
        longitude=37.6173,
        service_type=ServiceType.DRILLING
    )
    
    # Проверяем распределение
    assigned_contractor = await distribute_order(order, contractors)
    assert assigned_contractor.user.rating == 4.9  # Должен быть выбран подрядчик с лучшим рейтингом 