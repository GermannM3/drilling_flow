import os
import json
import uuid
import logging
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import time
from typing import Dict, List, Any, Optional, Tuple, Union
import re

# Импорт моделей
from models import User, Contractor, Order, OrderRating, ContractorStatus, OrderStatus, VerificationStatus

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Функция для преобразования URL SQLAlchemy в стандартный URL PostgreSQL
def convert_db_url(url):
    """Преобразует URL SQLAlchemy в стандартный URL PostgreSQL"""
    if url and 'postgresql+asyncpg://' in url:
        # Заменяем префикс
        return url.replace('postgresql+asyncpg://', 'postgresql://')
    return url

# Параметры подключения к базе данных Postgres
db_url = None

# Проверяем наличие переменных окружения для базы данных
if os.getenv("DATABASE_URL"):
    db_url = convert_db_url(os.getenv("DATABASE_URL"))
elif os.getenv("POSTGRES_URL"):
    db_url = convert_db_url(os.getenv("POSTGRES_URL"))
else:
    # Используем значение по умолчанию из переданных параметров
    db_url = "postgres://neondb_owner:npg_8BVv2yopUhON@ep-proud-glade-a5nte4bx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Выводим информацию о подключении (без пароля)
safe_url = re.sub(r':[^@]+@', ':***@', db_url)
logger.info(f"Используем URL базы данных: {safe_url}")

DATABASE_URL = db_url

# Имена таблиц
CONTRACTORS_TABLE = "contractors"
VERIFICATION_REQUESTS_TABLE = "verification_requests"
ORDERS_TABLE = "orders"
RATINGS_TABLE = "ratings"

class PostgresClient:
    """Класс для работы с Postgres"""
    
    def __init__(self, database_url):
        self.database_url = database_url
    
    def get_connection(self):
        """Получает соединение с базой данных"""
        try:
            conn = psycopg2.connect(self.database_url)
            return conn
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {str(e)}")
            return None
    
    def execute_query(self, query, params=None, fetch=True):
        """Выполняет SQL-запрос к базе данных"""
        conn = self.get_connection()
        if not conn:
            return False, {"error": "Не удалось подключиться к базе данных"}
        
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params or {})
                    
                    if fetch:
                        result = cursor.fetchall()
                        return True, result
                    
                    return True, {"message": "Запрос выполнен успешно"}
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {str(e)}")
            return False, {"error": str(e)}
        finally:
            conn.close()
    
    def get_item(self, table, id_field, id_value):
        """Получает элемент по ID"""
        query = f"SELECT * FROM {table} WHERE {id_field} = %s LIMIT 1"
        success, result = self.execute_query(query, (id_value,))
        
        if success and result and len(result) > 0:
            return True, dict(result[0])
        
        if success and not result:
            return False, {"error": f"Элемент с {id_field}={id_value} не найден"}
        
        return success, result
    
    def create_item(self, table, data):
        """Создает новый элемент в таблице"""
        # Удаляем None значения
        filtered_data = {k: v for k, v in data.items() if v is not None}
        
        fields = ", ".join(filtered_data.keys())
        placeholders = ", ".join([f"%({k})s" for k in filtered_data.keys()])
        
        query = f"INSERT INTO {table} ({fields}) VALUES ({placeholders}) RETURNING *"
        success, result = self.execute_query(query, filtered_data)
        
        return success
    
    def update_item(self, table, id_field, id_value, data):
        """Обновляет существующий элемент"""
        # Удаляем None значения
        filtered_data = {k: v for k, v in data.items() if v is not None and k != id_field}
        
        if not filtered_data:
            return True
        
        set_clause = ", ".join([f"{k} = %({k})s" for k in filtered_data.keys()])
        
        query = f"UPDATE {table} SET {set_clause} WHERE {id_field} = %(id_value)s RETURNING *"
        params = {**filtered_data, "id_value": id_value}
        
        success, result = self.execute_query(query, params)
        
        return success
    
    def delete_item(self, table, id_field, id_value):
        """Удаляет элемент по ID"""
        query = f"DELETE FROM {table} WHERE {id_field} = %s"
        success, result = self.execute_query(query, (id_value,), fetch=False)
        
        return success
    
    def list_items(self, table, filters=None, order=None, limit=None):
        """Получает список элементов с возможностью фильтрации и сортировки"""
        query = f"SELECT * FROM {table}"
        params = {}
        
        # Добавляем фильтрацию
        if filters:
            filter_clauses = []
            for i, (key, value) in enumerate(filters.items()):
                param_name = f"filter_{i}"
                filter_clauses.append(f"{key} = %({param_name})s")
                params[param_name] = value
            
            if filter_clauses:
                query += " WHERE " + " AND ".join(filter_clauses)
        
        # Добавляем сортировку
        if order:
            query += f" ORDER BY {order}"
        
        # Добавляем ограничение
        if limit:
            query += f" LIMIT {limit}"
        
        success, result = self.execute_query(query, params)
        
        if success and isinstance(result, list):
            return [dict(item) for item in result]
        
        return []

    def init_tables(self):
        """Инициализирует таблицы в базе данных, если они не существуют"""
        try:
            # Создаем таблицу подрядчиков
            self.execute_query(f"""
                CREATE TABLE IF NOT EXISTS {CONTRACTORS_TABLE} (
                    id UUID PRIMARY KEY,
                    user_id TEXT NOT NULL UNIQUE,
                    telegram_id TEXT,
                    full_name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    specialization TEXT NOT NULL,
                    work_radius FLOAT,
                    location JSONB,
                    status TEXT NOT NULL,
                    max_orders_per_day INTEGER DEFAULT 2,
                    rating FLOAT DEFAULT 5.0,
                    completed_orders INTEGER DEFAULT 0,
                    created_at BIGINT,
                    updated_at BIGINT
                )
            """, fetch=False)
            
            # Создаем таблицу запросов на верификацию
            self.execute_query(f"""
                CREATE TABLE IF NOT EXISTS {VERIFICATION_REQUESTS_TABLE} (
                    id UUID PRIMARY KEY,
                    contractor_id UUID NOT NULL REFERENCES {CONTRACTORS_TABLE}(id),
                    status TEXT NOT NULL,
                    documents JSONB,
                    comment TEXT,
                    created_at BIGINT,
                    updated_at BIGINT
                )
            """, fetch=False)
            
            # Создаем таблицу заказов
            self.execute_query(f"""
                CREATE TABLE IF NOT EXISTS {ORDERS_TABLE} (
                    order_id UUID PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    contractor_id UUID REFERENCES {CONTRACTORS_TABLE}(id),
                    title TEXT NOT NULL,
                    description TEXT,
                    location JSONB NOT NULL,
                    address TEXT,
                    specialization TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at BIGINT,
                    updated_at BIGINT,
                    completed_at BIGINT,
                    price FLOAT,
                    customer_rating INTEGER,
                    customer_feedback TEXT,
                    contractor_rating INTEGER,
                    contractor_feedback TEXT
                )
            """, fetch=False)
            
            # Создаем таблицу рейтингов
            self.execute_query(f"""
                CREATE TABLE IF NOT EXISTS {RATINGS_TABLE} (
                    id UUID PRIMARY KEY,
                    contractor_id UUID NOT NULL REFERENCES {CONTRACTORS_TABLE}(id),
                    order_id UUID NOT NULL REFERENCES {ORDERS_TABLE}(order_id),
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at BIGINT
                )
            """, fetch=False)
            
            logger.info("Таблицы успешно инициализированы")
            return True
        except Exception as e:
            logger.error(f"Ошибка при инициализации таблиц: {str(e)}")
            return False

# Создаем экземпляр клиента базы данных
db = PostgresClient(DATABASE_URL)

# Инициализируем таблицы при импорте модуля
try:
    db.init_tables()
except Exception as e:
    logger.error(f"Ошибка при инициализации таблиц: {str(e)}")

# Функции для работы с подрядчиками
def get_contractor(contractor_id):
    """Получает подрядчика по ID"""
    success, result = db.get_item("contractors", "id", contractor_id)
    
    if success and result:
        return True, Contractor.from_dict(result)
    
    return False, None

def get_contractor_by_user_id(user_id):
    """Получает подрядчика по ID пользователя"""
    # Создаем фильтр по user_id
    filters = {"user_id": user_id}
    
    # Получаем список подрядчиков с этим user_id (должен быть только один)
    contractors = db.list_items("contractors", filters)
    
    if contractors and len(contractors) > 0:
        return True, Contractor.from_dict(contractors[0])
    
    return False, None

def get_contractor_by_telegram_id(telegram_id):
    """Получает подрядчика по Telegram ID"""
    # Сначала получаем пользователя по telegram_id
    success, user = get_user_by_telegram_id(telegram_id)
    
    if not success or not user:
        return False, None
    
    # Затем получаем подрядчика по user_id
    return get_contractor_by_user_id(user.id)

def create_contractor(contractor):
    """Создает нового подрядчика в базе данных"""
    # Сохраняем в базу данных
    data = contractor.to_dict()
    success = db.create_item("contractors", data)
    
    return success, contractor

def update_contractor(contractor):
    """Обновляет данные подрядчика"""
    # Обновляем время изменения
    data = contractor.to_dict()
    success = db.update_item("contractors", "id", contractor.id, data)
    
    return success

def list_contractors(filters=None, order=None, limit=None):
    """Получает список подрядчиков с возможностью фильтрации и сортировки"""
    result = db.list_items("contractors", filters, order, limit)
    contractors = [Contractor.from_dict(item) for item in result]
    
    return contractors

# Функции для работы с запросами на верификацию
def create_verification_request(verification_request):
    """Создает новый запрос на верификацию"""
    # Генерируем UUID для запроса
    if not verification_request.id:
        verification_request.id = str(uuid.uuid4())
    
    # Сохраняем в базу данных
    data = verification_request.to_dict()
    success = db.create_item(VERIFICATION_REQUESTS_TABLE, data)
    
    return success, verification_request

def get_verification_request(request_id):
    """Получает запрос на верификацию по ID"""
    success, result = db.get_item(VERIFICATION_REQUESTS_TABLE, "id", request_id)
    
    if success and result:
        return True, VerificationRequest.from_dict(result)
    
    return False, None

def update_verification_status(request_id, status, comment=None):
    """Обновляет статус запроса на верификацию"""
    # Получаем текущий запрос
    success, request = get_verification_request(request_id)
    
    if not success or not request:
        return False
    
    # Обновляем статус и комментарий
    request.status = status
    if comment:
        request.comment = comment
    
    # Обновляем время изменения
    request.updated_at = int(time.time())
    
    # Сохраняем в базу данных
    data = request.to_dict()
    success = db.update_item(VERIFICATION_REQUESTS_TABLE, "id", request_id, data)
    
    return success

def list_pending_verification_requests():
    """Получает список незаконченных запросов на верификацию"""
    result = db.list_items(
        VERIFICATION_REQUESTS_TABLE,
        {"status": VerificationStatus.PENDING.value}
    )
    
    requests = [VerificationRequest.from_dict(item) for item in result]
    
    return requests

# Функции для работы с заказами
def create_order(order):
    """Создает новый заказ"""
    # Сохраняем в базу данных
    data = order.to_dict()
    success = db.create_item("orders", data)
    
    return success, order

def get_order(order_id):
    """Получает заказ по ID"""
    success, result = db.get_item("orders", "id", order_id)
    
    if success and result:
        return True, Order.from_dict(result)
    
    return False, None

def update_order(order):
    """Обновляет данные заказа"""
    # Обновляем время изменения
    order.updated_at = int(time.time())
    
    # Сохраняем в базу данных
    data = order.to_dict()
    success = db.update_item("orders", "id", order.id, data)
    
    return success

def assign_order_to_contractor(order_id, contractor_id):
    """Назначает заказ подрядчику"""
    # Получаем текущий заказ
    success, order = get_order(order_id)
    
    if not success or not order:
        return False
    
    # Обновляем данные заказа
    order.contractor_id = contractor_id
    order.status = OrderStatus.ASSIGNED
    order.updated_at = int(time.time())
    
    # Сохраняем в базу данных
    data = order.to_dict()
    success = db.update_item("orders", "id", order_id, data)
    
    return success

def list_orders(filters=None, order=None, limit=None):
    """Получает список заказов с возможностью фильтрации и сортировки"""
    result = db.list_items("orders", filters, order, limit)
    orders = [Order.from_dict(item) for item in result]
    
    return orders

def get_contractor_orders(contractor_id):
    """Получает список заказов подрядчика"""
    return list_orders({"contractor_id": contractor_id})

def list_available_orders(specialization=None):
    """Получает список доступных заказов для распределения"""
    filters = {"status": OrderStatus.CREATED.value}
    
    if specialization:
        filters["specialization"] = specialization.value
    
    return list_orders(filters)

# Функции для работы с рейтингами
def create_rating(rating):
    """Создает новую оценку заказа"""
    # Сохраняем в базу данных
    data = rating.to_dict()
    success = db.create_item("order_ratings", data)
    
    return success, rating

def get_rating(rating_id):
    """Получает оценку по ID"""
    success, result = db.get_item("order_ratings", "id", rating_id)
    
    if success and result:
        return True, OrderRating.from_dict(result)
    
    return False, None

def update_rating(rating):
    """Обновляет данные оценки"""
    # Сохраняем в базу данных
    data = rating.to_dict()
    success = db.update_item("order_ratings", "id", rating.id, data)
    
    return success

def list_ratings(filters=None, order=None, limit=None):
    """Получает список оценок с возможностью фильтрации и сортировки"""
    result = db.list_items("order_ratings", filters, order, limit)
    ratings = [OrderRating.from_dict(item) for item in result]
    
    return ratings

# Функции для работы с пользователями
def get_user_by_telegram_id(telegram_id):
    """Получает пользователя по Telegram ID"""
    # Создаем фильтр по telegram_id
    filters = {"telegram_id": telegram_id}
    
    # Получаем список пользователей с этим telegram_id (должен быть только один)
    users = db.list_items("users", filters)
    
    if users and len(users) > 0:
        return True, User.from_dict(users[0])
    
    return False, None

def create_user(user):
    """Создает нового пользователя в базе данных"""
    # Сохраняем в базу данных
    data = user.to_dict()
    success = db.create_item("users", data)
    
    return success, user

def update_user(user):
    """Обновляет данные пользователя"""
    # Сохраняем в базу данных
    data = user.to_dict()
    success = db.update_item("users", "id", user.id, data)
    
    return success 