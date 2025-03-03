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

def inspect_database():
    """Проверяет структуру таблиц в базе данных"""
    print(f"Подключение к базе данных...")
    
    try:
        # Проверяем соединение
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Подключение к базе данных успешно установлено")
        
        # Проверяем структуру таблиц
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Получаем список таблиц
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            tables = [table['table_name'] for table in cursor.fetchall()]
            print(f"Найдено таблиц: {len(tables)}")
            print(f"Таблицы: {', '.join(tables)}")
            
            # Проверяем структуру каждой таблицы
            for table in tables:
                print(f"\nСтруктура таблицы {table}:")
                
                # Получаем структуру таблицы
                cursor.execute(f"""
                    SELECT column_name, data_type, column_default, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                
                # Выводим информацию о столбцах
                for column in columns:
                    print(f"  {column['column_name']}: {column['data_type']} "
                          f"(null: {column['is_nullable']}, default: {column['column_default']})")
                
                # Получаем информацию о первичном ключе
                cursor.execute(f"""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_name = '{table}'
                """)
                
                pk_columns = cursor.fetchall()
                if pk_columns:
                    print(f"  Первичный ключ: {', '.join([col['column_name'] for col in pk_columns])}")
                else:
                    print("  Первичный ключ: не определен")
                
                # Получаем информацию о внешних ключах
                cursor.execute(f"""
                    SELECT kcu.column_name, ccu.table_name AS referenced_table, ccu.column_name AS referenced_column
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage ccu
                        ON tc.constraint_name = ccu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = '{table}'
                """)
                
                fk_columns = cursor.fetchall()
                if fk_columns:
                    print("  Внешние ключи:")
                    for fk in fk_columns:
                        print(f"    {fk['column_name']} -> {fk['referenced_table']}.{fk['referenced_column']}")
                else:
                    print("  Внешние ключи: не определены")
            
            # Проверяем наличие данных в таблицах
            print("\nКоличество записей в таблицах:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()['count']
                print(f"  {table}: {count}")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {str(e)}")
        return False

if __name__ == "__main__":
    print("Проверка структуры базы данных...")
    success = inspect_database()
    
    if success:
        print("\nПроверка завершена успешно!")
    else:
        print("\nПроверка завершена с ошибками. Исправьте их и попробуйте снова.") 