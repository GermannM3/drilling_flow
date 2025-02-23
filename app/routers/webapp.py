from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from ..core.config import get_settings, Settings
import os

router = APIRouter(tags=["webapp"])

# Путь к статическим файлам
static_path = Path(__file__).parent.parent / "static" / "webapp"
os.makedirs(str(static_path), exist_ok=True)

# Монтируем статические файлы
router.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@router.get("/", response_class=HTMLResponse)
async def get_webapp():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DrillFlow Dashboard</title>
        <link href="/static/style.css" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <div id="webcrumbs">
            <div class="min-h-screen bg-gradient-to-br from-emerald-800 to-blue-900 flex items-center justify-center p-4">
                <!-- Ваш HTML код здесь -->
            </div>
        </div>
    </body>
    </html>
    """

@router.get("/about")
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