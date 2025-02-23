"""
Настройка логирования
"""
import logging
from typing import Any

def setup_logging() -> Any:
    """
    Настройка логирования приложения
    Returns:
        Logger: Настроенный логгер
    """
    # Создаем логгер
    logger = logging.getLogger("drillflow")
    logger.setLevel(logging.INFO)

    # Создаем обработчик
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(handler)

    return logger 