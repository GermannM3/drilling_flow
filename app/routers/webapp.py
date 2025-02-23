from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
import logging
from ..core.bot import bot, dp
import hashlib
import hmac
from ..core.config import get_settings

router = APIRouter(tags=["webapp"])
logger = logging.getLogger(__name__)
settings = get_settings()

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
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DrillFlow Dashboard</title>
        <style>
            @import url(https://fonts.googleapis.com/css2?family=Roboto&display=swap);
            @import url(https://fonts.googleapis.com/css2?family=Inter&display=swap);
            @import url(https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200);
            
            body {
                margin: 0;
                font-family: Inter, sans-serif;
                background: linear-gradient(to bottom right, #065f46, #1e3a8a);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
            }
            
            .container {
                background: #0f172a;
                border-radius: 0.75rem;
                padding: 1.5rem;
                width: 100%;
                max-width: 1200px;
                border: 2px solid #10b981;
                color: #34d399;
            }
            
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 2rem;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .stat-card {
                background: #064e3b;
                padding: 1rem;
                border-radius: 0.5rem;
                border: 2px solid #10b981;
            }
            
            .button {
                background: #059669;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                border: none;
                cursor: pointer;
            }
            
            .button:hover {
                background: #047857;
            }
        </style>
        <script async src="https://telegram.org/js/telegram-widget.js?22" 
                data-telegram-login="Drill_Flow_bot" 
                data-size="large" 
                data-onauth="onTelegramAuth" 
                data-request-access="write">
        </script>
        <script type="text/javascript">
            function onTelegramAuth(user) {
                // Отправляем данные на сервер для проверки
                fetch('/auth/telegram', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(user)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('auth-section').style.display = 'none';
                        document.getElementById('dashboard').style.display = 'block';
                    }
                });
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div id="auth-section">
                <h1>Войдите через Telegram</h1>
                <!-- Виджет войдет сюда -->
            </div>
            
            <div id="dashboard" style="display: none;">
                <div class="header">
                    <h1>DrillFlow Dashboard</h1>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Активные Подрядчики</h3>
                        <p>247</p>
                    </div>
                    <div class="stat-card">
                        <h3>Выполненные Заказы</h3>
                        <p>1,893</p>
                    </div>
                    <div class="stat-card">
                        <h3>Ожидающие Заказы</h3>
                        <p>42</p>
                    </div>
                    <div class="stat-card">
                        <h3>Средний Рейтинг</h3>
                        <p>4.8</p>
                    </div>
                </div>
            </div>
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
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        logger.info(f"Received update: {update}")
        
        # Передаем обновление в диспетчер бота
        await dp.process_update(update)
        return JSONResponse({"ok": True})
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse({"error": str(e)}, status_code=500) 