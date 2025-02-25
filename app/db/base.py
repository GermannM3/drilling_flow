"""
Базовые классы для моделей БД
"""
from sqlalchemy.orm import declarative_base

# Создаем базовый класс для моделей
Base = declarative_base()

# Импорты моделей перенесены в конец файла, чтобы избежать циклических зависимостей
# Они будут импортированы только при необходимости создания таблиц

def import_models():
    """Импортирует все модели для создания таблиц"""
    from app.db.models.user import User
    from app.db.models.order import Order
    from app.db.models.rating import OrderRating
    from app.db.models.contractor import Contractor
    
    return [User, Order, OrderRating, Contractor] 