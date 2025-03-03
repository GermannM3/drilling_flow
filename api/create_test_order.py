import os
import sys
import json
import random
import time
import uuid
from datetime import datetime

# Добавляем путь к текущей директории в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем наши модули
from models import Order, OrderStatus, SpecializationType
from database import SupabaseClient, ORDERS_TABLE, CONTRACTORS_TABLE
from order_handlers import distribute_order

# Получаем параметры доступа к Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-supabase-url.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-key")

def create_test_order():
    """Создаём тестовый заказ и распределяем его между подрядчиками"""
    print("Создание тестового заказа...")
    
    # Создаём клиент для работы с базой данных
    db = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    
    # Проверяем наличие активных подрядчиков
    contractors = db.list_items(CONTRACTORS_TABLE, {"status": "ACTIVE"})
    if not contractors:
        print("Нет активных подрядчиков! Заказ не может быть распределён.")
        return
    
    print(f"Найдено активных подрядчиков: {len(contractors)}")
    
    # Создаём тестовый заказ
    order_id = str(uuid.uuid4())
    now = int(time.time())
    
    # Выбираем случайную специализацию
    specialization = random.choice([
        SpecializationType.DRILLING, 
        SpecializationType.SEWERAGE, 
        SpecializationType.BOTH
    ])
    
    # Выбираем случайное местоположение в пределах Москвы
    # (55.751244, 37.618423) - координаты центра Москвы
    lat = 55.751244 + (random.random() - 0.5) * 0.1  # +/- ~5км
    lng = 37.618423 + (random.random() - 0.5) * 0.1  # +/- ~5км
    
    # Создаём объект заказа
    order = Order(
        order_id=order_id,
        customer_id="test_customer",
        title=f"Тестовый заказ {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        description="Это тестовый заказ для проверки системы распределения заказов",
        location={"lat": lat, "lng": lng},
        specialization=specialization,
        status=OrderStatus.CREATED,
        created_at=now,
        updated_at=now,
        price=random.randint(5000, 50000),  # Случайная цена между 5000 и 50000 рублей
        address="г. Москва, Тестовая улица, 123"
    )
    
    # Сохраняем заказ в базе данных
    success = db.create_item(ORDERS_TABLE, order.to_dict())
    
    if success:
        print(f"Заказ успешно создан с ID: {order_id}")
        
        # Распределяем заказ между подрядчиками
        print("Распределение заказа...")
        
        # Получаем токен бота
        token = os.getenv("BOT_TOKEN", "")
        if not token:
            print("Ошибка: не указан токен бота (BOT_TOKEN)")
            return
        
        # Распределяем заказ
        distribute_order(order, token)
        
        print("Заказ успешно распределён!")
    else:
        print("Ошибка при создании заказа!")

if __name__ == "__main__":
    create_test_order() 