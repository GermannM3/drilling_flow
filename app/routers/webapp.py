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
from ..services.auth import get_current_user

router = APIRouter(tags=["webapp"])
logger = logging.getLogger(__name__)
settings = get_settings()

# Определяем пути к статическим файлам
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static" / "webapp"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Монтируем статические файлы
router.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

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
async def get_webapp():
    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DrillFlow Dashboard</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <link rel="stylesheet" href="/static/webapp/style.css">
        <script>
            // Инициализация Telegram WebApp
            let tg = window.Telegram.WebApp;
            tg.expand();
            
            // Функция для отправки заказа
            async function submitOrder(form) {{
                let formData = new FormData(form);
                let data = {{}};
                formData.forEach((value, key) => data[key] = value);
                
                try {{
                    let response = await fetch('/api/orders/create', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${{tg.initData}}`
                        }},
                        body: JSON.stringify(data)
                    }});
                    
                    let result = await response.json();
                    if (result.status === 'success') {{
                        tg.showPopup({{
                            title: 'Успех',
                            message: 'Заказ успешно создан!',
                            buttons: [{{type: 'ok'}}]
                        }});
                    }}
                }} catch (error) {{
                    tg.showAlert('Ошибка при создании заказа: ' + error.message);
                }}
                return false;
            }}
            
            // Функция для регистрации
            async function register() {{
                try {{
                    let userData = {{
                        telegram_id: tg.initDataUnsafe.user.id,
                        username: tg.initDataUnsafe.user.username,
                        first_name: tg.initDataUnsafe.user.first_name
                    }};
                    
                    let response = await fetch('/api/auth/register', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify(userData)
                    }});
                    
                    let result = await response.json();
                    if (result.status === 'success') {{
                        tg.showPopup({{
                            title: 'Успех',
                            message: 'Регистрация успешна!',
                            buttons: [{{type: 'ok'}}]
                        }});
                    }}
                }} catch (error) {{
                    tg.showAlert('Ошибка при регистрации: ' + error.message);
                }}
            }}
        </script>
    </head>
    <body>
        <div id="app">
            <form id="orderForm" onsubmit="return submitOrder(this);">
                <h2>Создать заказ</h2>
                <div class="form-group">
                    <label>Тип работ</label>
                    <select name="service_type" required>
                        <option value="drilling">Бурение скважины</option>
                        <option value="repair">Ремонт оборудования</option>
                        <option value="maintenance">Обслуживание</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Адрес</label>
                    <input type="text" name="address" required>
                </div>
                <div class="form-group">
                    <label>Описание</label>
                    <textarea name="description" required></textarea>
                </div>
                <button type="submit">Отправить заказ</button>
            </form>
            
            <button onclick="register()">Зарегистрироваться через Telegram</button>
        </div>
    </body>
    </html>
    """

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