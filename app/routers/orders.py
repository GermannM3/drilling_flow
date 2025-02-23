from fastapi import APIRouter, Depends
from ..core.config import get_settings, Settings

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.get("/")
async def get_orders(settings: Settings = Depends(get_settings)):
    """Получение списка заказов"""
    return {"message": "Orders list"} 