"""
Проверка здоровья сервиса
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .config import get_settings, Settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Проверка здоровья сервиса
    Returns:
        dict: Статус компонентов системы
    """
    try:
        # Проверка соединения с БД
        await db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "version": settings.VERSION,
        "database": db_status,
        "environment": "testing" if settings.TESTING else "production"
    } 