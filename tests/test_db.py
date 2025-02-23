import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.order import Order
from app.models.contractor import Contractor

@pytest.fixture
async def db_session():
    """Фикстура для тестовой базы данных"""
    async for session in get_db():
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_create_order(db_session: AsyncSession):
    """Тест создания заказа"""
    order = Order(
        client_id=1,
        service_type="drilling",
        location="55.7558,37.6173",
        description="Test order"
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    assert order.id is not None

@pytest.mark.asyncio
async def test_contractor_rating(db_session: AsyncSession):
    """Тест системы рейтинга"""
    contractor = Contractor(
        user_id=1,
        name="Test Contractor",
        rating=4.5,
        orders_completed=10
    )
    db_session.add(contractor)
    await db_session.commit()
    
    # Проверка обновления рейтинга
    contractor.rating = (contractor.rating * contractor.orders_completed + 5) / (contractor.orders_completed + 1)
    contractor.orders_completed += 1
    await db_session.commit()
    await db_session.refresh(contractor)
    assert contractor.orders_completed == 11
    assert 4.5 <= contractor.rating <= 5.0 