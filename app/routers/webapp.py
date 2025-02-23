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
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DrillFlow Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
        <script async src="https://telegram.org/js/telegram-widget.js?22" 
                data-telegram-login="Drill_Flow_bot" 
                data-size="large" 
                data-onauth="onTelegramAuth" 
                data-request-access="write">
        </script>
        <style>
            /* Весь ваш CSS код */
            #webcrumbs { font-family: Inter !important; font-size: 18px !important; }
            #webcrumbs .min-h-screen { min-height: 100vh; }
            #webcrumbs .bg-gradient-to-br { background-image: linear-gradient(to bottom right, var(--tw-gradient-stops)); }
            #webcrumbs .from-emerald-800 { --tw-gradient-from: #065f46; }
            #webcrumbs .to-blue-900 { --tw-gradient-to: #1e3a8a; }
            /* ... остальные стили из вашего CSS ... */
        </style>
        <script>
            function onTelegramAuth(user) {
                fetch('/auth/telegram', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
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
        <div id="webcrumbs">
            <div class="min-h-screen bg-gradient-to-br from-emerald-800 to-blue-900 flex items-center justify-center p-4 sm:p-8">
                <div class="w-full max-w-[1200px] bg-slate-900 rounded-xl shadow-2xl p-4 sm:p-8 border-2 sm:border-4 border-emerald-500">
                    <header class="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
                        <div class="flex items-center gap-4">
                            <span class="material-symbols-outlined text-3xl sm:text-4xl text-emerald-400">water_drop</span>
                            <h1 class="text-2xl sm:text-3xl font-bold text-emerald-400">Панель Управления DrillFlow</h1>
                        </div>
                        <div class="flex items-center gap-4">
                            <details class="relative">
                                <summary class="flex items-center gap-2 cursor-pointer hover:bg-emerald-800 p-2 rounded-lg transition-all">
                                    <span class="material-symbols-outlined text-emerald-400">notifications</span>
                                    <span class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">3</span>
                                </summary>
                                <div class="absolute right-0 mt-2 w-64 bg-slate-800 rounded-lg shadow-2xl p-4 z-10 border-2 border-emerald-500">
                                    <div class="flex flex-col gap-2">
                                        <div class="p-2 hover:bg-slate-700 rounded-lg transition-all text-emerald-400">
                                            <p class="font-semibold">Новый Заказ #1234</p>
                                            <p class="text-sm text-emerald-300">Запрос на бурение скважины - 5км</p>
                                        </div>
                                    </div>
                                </div>
                            </details>
                        </div>
                    </header>

                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
                        <!-- Карточки статистики -->
                        <div class="bg-emerald-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500">
                            <!-- ... и так далее для всех карточек ... -->
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
                        <!-- Секции с заказами и подрядчиками -->
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
        await dp.process_update(update)
        return JSONResponse({"ok": True})
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JSONResponse({"error": str(e)}, status_code=500) 