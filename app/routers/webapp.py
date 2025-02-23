from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from ..core.config import get_settings, Settings
import os

router = APIRouter(tags=["webapp"])

# Закомментируйте эти строки
# static_path = Path(__file__).parent.parent / "static" / "webapp"
# os.makedirs(str(static_path), exist_ok=True)
# router.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@router.get("/")
async def get_webapp(settings: Settings = Depends(get_settings)):
    """Получение веб-интерфейса"""
    return {"message": "Web interface"}

router = APIRouter(prefix="/about", tags=["about"])

@router.get("")
async def get_about():
    return JSONResponse({
        "app_name": "DrillFlow",
        "version": "1.0.0",
        "legal": {
            "maps_terms": "https://yandex.ru/legal/maps_api/",
            "maps_attribution": "© Яндекс Карты",
        },
        "contacts": {
            "email": "support@drillflow.ru",
            "telegram": "https://t.me/drillflow_bot"
        }
    }) 