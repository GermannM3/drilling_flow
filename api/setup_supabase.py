import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# Добавляем путь к текущей директории в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем константы из database.py
from database import (
    DATABASE_URL,
    CONTRACTORS_TABLE,
    VERIFICATION_REQUESTS_TABLE,
    ORDERS_TABLE,
    RATINGS_TABLE
)

def check_database_connection():
    """Проверяет подключение к PostgreSQL и наличие необходимых таблиц"""
    print(f"Проверка подключения к базе данных URL: {DATABASE_URL}")
    
    if not DATABASE_URL:
        print("Ошибка: не указаны параметры подключения к базе данных")
        print("Установите переменную окружения DATABASE_URL")
        return False
    
    try:
        # Проверяем соединение
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Подключение к базе данных успешно установлено")
        
        # Проверяем наличие необходимых таблиц
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            existing_tables = [table['table_name'] for table in cursor.fetchall()]
            
            print(f"Найдено таблиц: {len(existing_tables)}")
            
            required_tables = [
                CONTRACTORS_TABLE,
                VERIFICATION_REQUESTS_TABLE,
                ORDERS_TABLE,
                RATINGS_TABLE
            ]
            
            missing_tables = []
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ Таблица {table} существует")
                else:
                    print(f"❌ Таблица {table} отсутствует")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\nНеобходимо создать таблицы: {', '.join(missing_tables)}")
                
                # Создаем отсутствующие таблицы
                create_missing_tables(conn, missing_tables)
            else:
                print("\nВсе необходимые таблицы существуют")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"❌ Ошибка при подключении к базе данных: {str(e)}")
        return False

def create_missing_tables(conn, missing_tables):
    """Создает отсутствующие таблицы в базе данных"""
    for table in missing_tables:
        print(f"\nСоздание таблицы {table}...")
        
        # Определяем структуру таблицы в зависимости от её типа
        if table == CONTRACTORS_TABLE:
            create_contractors_table(conn)
        elif table == VERIFICATION_REQUESTS_TABLE:
            create_verification_requests_table(conn)
        elif table == ORDERS_TABLE:
            create_orders_table(conn)
        elif table == RATINGS_TABLE:
            create_ratings_table(conn)

def create_contractors_table(conn):
    """Создает таблицу contractors в базе данных"""
    # Формируем SQL-запрос для создания таблицы contractors
    sql = f"""
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
    );
    """
    
    # Выполняем SQL-запрос
    execute_sql(conn, sql)

def create_verification_requests_table(conn):
    """Создает таблицу verification_requests в базе данных"""
    # Формируем SQL-запрос для создания таблицы verification_requests
    sql = f"""
    CREATE TABLE IF NOT EXISTS {VERIFICATION_REQUESTS_TABLE} (
        id UUID PRIMARY KEY,
        contractor_id UUID NOT NULL REFERENCES {CONTRACTORS_TABLE}(id),
        status TEXT NOT NULL,
        documents JSONB,
        comment TEXT,
        created_at BIGINT,
        updated_at BIGINT
    );
    """
    
    # Выполняем SQL-запрос
    execute_sql(conn, sql)

def create_orders_table(conn):
    """Создает таблицу orders в базе данных"""
    # Формируем SQL-запрос для создания таблицы orders
    sql = f"""
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
    );
    """
    
    # Выполняем SQL-запрос
    execute_sql(conn, sql)

def create_ratings_table(conn):
    """Создает таблицу ratings в базе данных"""
    # Формируем SQL-запрос для создания таблицы ratings
    sql = f"""
    CREATE TABLE IF NOT EXISTS {RATINGS_TABLE} (
        id UUID PRIMARY KEY,
        contractor_id UUID NOT NULL REFERENCES {CONTRACTORS_TABLE}(id),
        order_id UUID NOT NULL REFERENCES {ORDERS_TABLE}(order_id),
        rating INTEGER NOT NULL,
        comment TEXT,
        created_at BIGINT
    );
    """
    
    # Выполняем SQL-запрос
    execute_sql(conn, sql)

def execute_sql(conn, sql):
    """Выполняет SQL-запрос"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
        conn.commit()
        print("✅ SQL-запрос выполнен успешно")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка выполнения SQL-запроса: {str(e)}")
        return False

if __name__ == "__main__":
    print("Проверка базы данных и настройка таблиц...")
    success = check_database_connection()
    
    if success:
        print("\nВсе проверки завершены успешно!")
    else:
        print("\nПроверка завершена с ошибками. Исправьте их и попробуйте снова.") 