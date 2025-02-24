"""
Базовые классы для моделей БД
"""
from sqlalchemy.orm import declarative_base

# Создаем базовый класс для моделей
Base = declarative_base()

# Импортируем все модели здесь, чтобы они были доступны при создании таблиц
from app.db.models.user import User
from app.db.models.order import Order
from app.db.models.rating import OrderRating
from app.db.models.contractor import Contractor 