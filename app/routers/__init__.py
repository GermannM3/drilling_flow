"""
Инициализация роутеров
"""
from fastapi import APIRouter
from .webapp import router as webapp_router
from .auth import router as auth_router
from .orders import router as orders_router
from .contractors import router as contractors_router
from .geo import router as geo_router
from .bot import router as bot_router

# Создаем основной роутер
router = APIRouter()

# Подключаем все роутеры
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(orders_router, prefix="/orders", tags=["orders"])
router.include_router(contractors_router, prefix="/contractors", tags=["contractors"])
router.include_router(geo_router, prefix="/geo", tags=["geo"])
router.include_router(bot_router, prefix="/api", tags=["bot"])
router.include_router(webapp_router, tags=["webapp"]) 