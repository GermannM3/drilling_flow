from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
import logging
from ..core.bot import bot, dp
import hashlib
import hmac
from ..core.config import get_settings
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from ..services.geo import YandexGeoService
from ..db.models import Order, ServiceType, User
from app.services.auth import get_current_user
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["webapp"])
logger = logging.getLogger(__name__)
settings = get_settings()

# Определяем пути к статическим файлам
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static" / "webapp"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Монтируем статические файлы
router.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Путь к директории с шаблонами
templates = Jinja2Templates(directory="app/templates")

def check_telegram_auth(auth_data):
    """Проверка данных авторизации от Telegram"""
    check_hash = auth_data.pop('hash')
    data_check_arr = []
    
    for key, value in sorted(auth_data.items()):
        data_check_arr.append(f"{key}={value}")
    
    data_check_string = '\n'.join(data_check_arr)
    secret_key = hashlib.sha256(settings.TELEGRAM_TOKEN.encode()).digest()
    hash_string = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    return hash_string == check_hash

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Главная страница веб-приложения
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@router.post("/auth/telegram")
async def telegram_auth(request: Request):
    try:
        auth_data = await request.json()
        if check_telegram_auth(auth_data):
            return JSONResponse({"success": True})
        return JSONResponse({"success": False, "error": "Invalid authentication"})
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return JSONResponse({"success": False, "error": str(e)})

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

@router.post("/webhook")
async def webhook(update: dict):
    """Обработчик вебхуков от Telegram"""
    try:
        # Обрабатываем обновление
        await dp.feed_webhook_update(update)
        return JSONResponse({"status": "ok"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/auth/register")
async def register_user(user_data: dict):
    """Регистрация пользователя"""
    try:
        # Здесь будет логика регистрации
        return {"status": "success", "message": "Регистрация успешна"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/orders/create")
async def create_order(
    order_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Создание заказа"""
    try:
        # Здесь будет логика создания заказа
        return {"status": "success", "order_id": 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_orders():
    """Получение списка заказов"""
    return {"orders": []}

@router.get("/api/orders/active")
async def get_active_orders():
    # Заглушка для демонстрации
    return JSONResponse([
        {"id": 1, "title": "Бурение скважины", "location": "ул. Центральная 1"},
        {"id": 2, "title": "Ремонт оборудования", "location": "пр. Ленина 42"},
        {"id": 3, "title": "Геологическая разведка", "location": "ул. Полевая 15"}
    ]) 