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
from ..db.models import Order, ServiceType, User, OrderStatus
from app.services.auth import get_current_user
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rating import get_contractor_rating

router = APIRouter(tags=["webapp"])
logger = logging.getLogger(__name__)
settings = get_settings()

# Определяем пути к статическим файлам
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static" / "webapp"
TEMPLATES_DIR = BASE_DIR / "templates"

# Монтируем статические файлы
router.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Инициализируем шаблоны
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

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
async def index(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Главная страница"""
    # Получаем топ подрядчиков по рейтингу
    top_contractors = await get_contractor_rating(db, limit=5)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "contractors": top_contractors
        }
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание заказа"""
    try:
        new_order = Order(
            client_id=current_user.id,
            service_type=order_data.get("service_type"),
            description=order_data.get("description"),
            address=order_data.get("address"),
            status=OrderStatus.NEW
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return {"status": "success", "order_id": new_order.id}
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка заказов"""
    orders = db.query(Order).filter(
        Order.client_id == current_user.id
    ).all()
    return {"orders": [order.__dict__ for order in orders]}

@router.get("/api/orders/active")
async def get_active_orders(db: Session = Depends(get_db)):
    """Получение активных заказов"""
    active_orders = db.query(Order).filter(
        Order.status == OrderStatus.NEW
    ).all()
    return JSONResponse([{
        "id": order.id,
        "title": order.description,
        "location": order.address
    } for order in active_orders])

@router.get("/webapp", response_class=HTMLResponse)
async def webapp(request: Request):
    """Рендеринг веб-приложения"""
    try:
        return templates.TemplateResponse(
            "webapp.html",
            {"request": request}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/orders")
async def get_orders():
    """API для получения заказов"""
    try:
        # Заглушка для тестирования
        return {
            "orders": [
                {"title": "Тестовый заказ 1", "location": "Москва"},
                {"title": "Тестовый заказ 2", "location": "Санкт-Петербург"}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 