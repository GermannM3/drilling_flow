"""
Инициализация роутеров приложения
"""
from .orders import router as orders
from .contractors import router as contractors
from .auth import router as auth
from .geo import router as geo
from .webapp import router as webapp

__all__ = ["orders", "contractors", "auth", "geo", "webapp"] 