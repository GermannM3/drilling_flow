"""
Точка входа для Vercel Serverless Functions
"""
import os
import sys
import logging
import traceback
from mangum import Mangum
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Логируем информацию о среде запуска
logger.debug(f"Python version: {sys.version}")
logger.debug(f"Current directory: {os.getcwd()}")
logger.debug(f"Environment variables: {dict(os.environ)}")

# Создаем приложение
app = FastAPI(title="DrillFlow Webhook Handler")

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Эндпоинт для проверки работоспособности"""
    return {"status": "ok", "message": "DrillFlow webhook handler is running"}

@app.post("/webhook")
async def webhook(request: Request):
    """Обработчик webhook-запросов"""
    logger.info("Received webhook request")
    
    try:
        # Логируем заголовки запроса
        headers = dict(request.headers)
        logger.debug(f"Request headers: {headers}")
        
        # Получаем тело запроса
        body = await request.json()
        logger.info(f"Request body: {body}")
        
        return {
            "status": "success",
            "message": "Webhook processed successfully",
            "data": body
        }
        
    except Exception as e:
        # Детальное логирование ошибки
        logger.error(f"Error processing webhook: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error",
                "error": str(e),
                "type": type(e).__name__
            }
        )

# Создаем ASGI-обработчик
handler = Mangum(app, lifespan="off") 