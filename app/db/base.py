"""
Базовые классы для моделей БД
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass 