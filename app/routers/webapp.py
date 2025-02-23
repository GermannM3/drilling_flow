from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
import logging
from ..core.bot import bot
from ..core.bot import dp

router = APIRouter(tags=["webapp"])

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>DrillFlow Dashboard</h1>
                <button class="button">Войти</button>
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