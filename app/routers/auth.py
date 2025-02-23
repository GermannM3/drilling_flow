from fastapi import APIRouter, Depends
from ..core.config import get_settings, Settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
async def login(settings: Settings = Depends(get_settings)):
    """Авторизация пользователя"""
    return {"message": "Login endpoint"} 