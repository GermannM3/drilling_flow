from fastapi import APIRouter, Depends
from ..core.config import get_settings, Settings

router = APIRouter(prefix="/api/contractors", tags=["contractors"])

@router.get("/")
async def get_contractors(settings: Settings = Depends(get_settings)):
    """Получение списка подрядчиков"""
    return {"message": "Contractors list"} 