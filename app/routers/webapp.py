"""
Роутер для веб-интерфейса
"""
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
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    """Главная страница"""
    try:
        # Получаем статистику
        contractors_count = await db.execute("SELECT COUNT(*) FROM contractors")
        contractors_count = contractors_count.scalar() or 0
        
        orders_completed = await db.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
        orders_completed = orders_completed.scalar() or 0
        
        orders_pending = await db.execute("SELECT COUNT(*) FROM orders WHERE status = 'new'")
        orders_pending = orders_pending.scalar() or 0
        
        avg_rating = await db.execute("SELECT AVG(rating) FROM contractors")
        avg_rating = round(avg_rating.scalar() or 0, 1)
        
        # Получаем последние заказы
        latest_orders = await db.execute(
            "SELECT id, title, location, status FROM orders ORDER BY created_at DESC LIMIT 5"
        )
        latest_orders = latest_orders.fetchall()
        
        # Получаем лучших подрядчиков
        top_contractors = await db.execute(
            "SELECT c.id, u.full_name, c.rating FROM contractors c "
            "JOIN users u ON c.user_id = u.id "
            "ORDER BY c.rating DESC LIMIT 5"
        )
        top_contractors = top_contractors.fetchall()
        
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request,
                "contractors_count": contractors_count,
                "orders_completed": orders_completed,
                "orders_pending": orders_pending,
                "avg_rating": avg_rating,
                "latest_orders": latest_orders,
                "top_contractors": top_contractors
            }
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        # В случае ошибки отображаем страницу без данных из БД
        return templates.TemplateResponse("index.html", {"request": request})

@router.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница заказов"""
    try:
        # Получаем все заказы
        orders = await db.execute(
            "SELECT id, title, location, status, created_at FROM orders ORDER BY created_at DESC"
        )
        orders = orders.fetchall()
        
        return templates.TemplateResponse(
            "orders.html", 
            {
                "request": request,
                "orders": orders
            }
        )
    except Exception as e:
        logger.error(f"Error rendering orders page: {e}")
        # В случае ошибки отображаем страницу с заглушкой
        return templates.TemplateResponse("orders.html", {"request": request})

@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail(order_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Детальная страница заказа"""
    try:
        # Получаем заказ по ID
        order = await db.execute(
            "SELECT id, title, description, location, status, created_at FROM orders WHERE id = :order_id",
            {"order_id": order_id}
        )
        order = order.fetchone()
        
        if not order:
            # Если заказ не найден, возвращаем 404
            return templates.TemplateResponse(
                "404.html", 
                {"request": request, "message": f"Заказ с ID {order_id} не найден"},
                status_code=404
            )
        
        return templates.TemplateResponse(
            "order_detail.html", 
            {
                "request": request,
                "order": order
            }
        )
    except Exception as e:
        logger.error(f"Error rendering order detail page: {e}")
        # В случае ошибки отображаем страницу с заглушкой
        return templates.TemplateResponse("order_detail.html", {"request": request})

@router.get("/contractors", response_class=HTMLResponse)
async def contractors_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница подрядчиков"""
    try:
        # Получаем всех подрядчиков
        contractors = await db.execute(
            "SELECT c.id, u.full_name, c.rating, c.orders_completed "
            "FROM contractors c JOIN users u ON c.user_id = u.id "
            "ORDER BY c.rating DESC"
        )
        contractors = contractors.fetchall()
        
        return templates.TemplateResponse(
            "contractors.html", 
            {
                "request": request,
                "contractors": contractors
            }
        )
    except Exception as e:
        logger.error(f"Error rendering contractors page: {e}")
        # В случае ошибки отображаем страницу с заглушкой
        return templates.TemplateResponse("contractors.html", {"request": request})

@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """Страница о нас"""
    return templates.TemplateResponse(
        "about.html", 
        {
            "request": request,
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

@router.get("/webapp", response_class=HTMLResponse)
async def webapp(request: Request):
    """Веб-приложение для Telegram"""
    return templates.TemplateResponse(
        "webapp.html",
        {
            "request": request,
            "page": "webapp"
        }
    ) 