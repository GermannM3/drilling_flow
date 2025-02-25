#!/usr/bin/env python
"""
Скрипт для запуска миграций

Примеры использования:
- python scripts/migrate.py revision --autogenerate -m "initial migration"
- python scripts/migrate.py upgrade head
"""
import os
import sys
import argparse
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from alembic.config import Config
from alembic import command

from app.core.config import get_settings

def main():
    """
    Основная функция для запуска миграций
    """
    parser = argparse.ArgumentParser(description="Запуск миграций Alembic")
    parser.add_argument('command', choices=['revision', 'upgrade', 'downgrade', 'heads', 'show'], 
                        help='Команда Alembic (revision, upgrade, downgrade, heads, show)')
    parser.add_argument('args', nargs='*', help='Аргументы для команды')
    parser.add_argument('-m', '--message', help='Сообщение для миграции (для команды revision)')
    parser.add_argument('--autogenerate', action='store_true', help='Автоматически генерировать миграцию')
    
    args = parser.parse_args()
    
    settings = get_settings()
    
    # Настраиваем Alembic
    alembic_cfg = Config("alembic.ini")
    
    # Запускаем нужную команду
    if args.command == 'revision':
        command.revision(alembic_cfg, message=args.message, autogenerate=args.autogenerate)
    
    elif args.command == 'upgrade':
        if not args.args:
            print("Ошибка: нужно указать revision (например, 'head')")
            sys.exit(1)
        command.upgrade(alembic_cfg, args.args[0])
    
    elif args.command == 'downgrade':
        if not args.args:
            print("Ошибка: нужно указать revision для отката")
            sys.exit(1)
        command.downgrade(alembic_cfg, args.args[0])
    
    elif args.command == 'heads':
        command.heads(alembic_cfg)
    
    elif args.command == 'show':
        if not args.args:
            print("Ошибка: нужно указать revision для показа")
            sys.exit(1)
        command.show(alembic_cfg, args.args[0])

if __name__ == "__main__":
    main() 