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
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            /* Импорт стилей */
            @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Inter&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
            
            /* Базовые стили */
            #webcrumbs { font-family: Inter !important; font-size: 18px !important; }
            #webcrumbs .min-h-screen { min-height: 100vh; }
            #webcrumbs .bg-gradient-to-br { background-image: linear-gradient(to bottom right, var(--tw-gradient-stops)); }
            #webcrumbs .from-emerald-800 { --tw-gradient-from: #065f46; }
            #webcrumbs .to-blue-900 { --tw-gradient-to: #1e3a8a; }
            /* ... весь остальной CSS ... */
        </style>
    </head>
    <body>
        <div id="webcrumbs">
            <div class="min-h-screen bg-gradient-to-br from-emerald-800 to-blue-900 flex items-center justify-center p-4">
                <div class="w-full max-w-[1200px] bg-slate-900 rounded-xl shadow-2xl p-4 border-2 border-emerald-500">
                    <header class="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
                        <div class="flex items-center gap-4">
                            <span class="material-symbols-outlined text-3xl text-emerald-400">water_drop</span>
                            <h1 class="text-2xl font-bold text-emerald-400">Панель Управления DrillFlow</h1>
                        </div>
                        <div class="flex items-center gap-4">
                            <button onclick="createOrder()" class="bg-emerald-600 text-white px-3 py-1 rounded-lg hover:bg-emerald-700 transition-all transform hover:scale-105 border-2 border-emerald-400">
                                Создать заказ
                            </button>
                        </div>
                    </header>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div class="bg-slate-800 rounded-xl border-2 border-emerald-500 p-4">
                            <h2 class="text-lg font-bold mb-4 text-emerald-400">Активные заказы</h2>
                            <div class="space-y-4" id="activeOrders">
                                <!-- Заказы будут добавляться динамически -->
                            </div>
                        </div>

                        <div class="bg-slate-800 rounded-xl border-2 border-emerald-500 p-4">
                            <h2 class="text-lg font-bold mb-4 text-emerald-400">Лучшие подрядчики</h2>
                            <div class="space-y-4" id="topContractors">
                                <!-- Подрядчики будут добавляться динамически -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let tg = window.Telegram.WebApp;
            tg.expand();

            // Загрузка активных заказов
            async function loadActiveOrders() {
                try {
                    const response = await fetch('/api/orders/active');
                    const orders = await response.json();
                    const container = document.getElementById('activeOrders');
                    
                    orders.forEach(order => {
                        const orderElement = document.createElement('div');
                        orderElement.className = 'flex items-center justify-between p-2 hover:bg-slate-700 rounded-lg transition-all';
                        orderElement.innerHTML = `
                            <div class="flex items-center gap-4">
                                <span class="material-symbols-outlined text-emerald-400">drill</span>
                                <div>
                                    <p class="font-semibold text-emerald-400">${order.title}</p>
                                    <p class="text-xs text-emerald-300">${order.location}</p>
                                </div>
                            </div>
                            <button onclick="assignOrder(${order.id})" class="bg-emerald-600 text-white px-3 py-1 rounded-lg hover:bg-emerald-700 transition-all transform hover:scale-105 border-2 border-emerald-400">
                                Назначить
                            </button>
                        `;
                        container.appendChild(orderElement);
                    });
                } catch (error) {
                    console.error('Ошибка загрузки заказов:', error);
                }
            }

            // Создание нового заказа
            function createOrder() {
                tg.showPopup({
                    title: 'Создание заказа',
                    message: 'Введите детали заказа',
                    buttons: [
                        {id: 'cancel', type: 'cancel', text: 'Отмена'},
                        {id: 'create', type: 'default', text: 'Создать'}
                    ]
                }, function(buttonId) {
                    if (buttonId === 'create') {
                        // Отправка данных на сервер
                        fetch('/api/orders/create', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                // Данные заказа
                            })
                        });
                    }
                });
            }

            // Назначение подрядчика на заказ
            function assignOrder(orderId) {
                tg.showPopup({
                    title: 'Назначение подрядчика',
                    message: 'Выберите подрядчика для заказа',
                    buttons: [
                        {id: 'cancel', type: 'cancel', text: 'Отмена'},
                        {id: 'assign', type: 'default', text: 'Назначить'}
                    ]
                });
            }

            // Загрузка данных при старте
            document.addEventListener('DOMContentLoaded', () => {
                loadActiveOrders();
            });
        </script>
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

@router.post("/api/orders/create")
async def create_order(request: Request):
    try:
        data = await request.json()
        # Обработка создания заказа
        return JSONResponse({"success": True})
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return JSONResponse({"success": False, "error": str(e)})

@router.get("/api/orders/active")
async def get_active_orders():
    # Заглушка для демонстрации
    return JSONResponse([
        {"id": 1, "title": "Бурение скважины", "location": "ул. Центральная 1"},
        {"id": 2, "title": "Ремонт оборудования", "location": "пр. Ленина 42"},
        {"id": 3, "title": "Геологическая разведка", "location": "ул. Полевая 15"}
    ]) 