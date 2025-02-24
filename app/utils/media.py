"""
Утилиты для работы с медиафайлами
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.core.config import get_settings

settings = get_settings()

def get_media_path(folder: str) -> Path:
    """
    Получение пути к директории медиафайлов
    
    Args:
        folder: Поддиректория (avatars, orders, temp)
    
    Returns:
        Path: Путь к директории
    """
    return Path(settings.MEDIA_ROOT) / folder

def generate_unique_filename(filename: str) -> str:
    """
    Генерация уникального имени файла
    
    Args:
        filename: Исходное имя файла
    
    Returns:
        str: Уникальное имя файла
    """
    ext = filename.split('.')[-1]
    return f"{uuid.uuid4()}.{ext}"

async def save_upload_file(file: UploadFile, folder: str) -> str:
    """
    Сохранение загруженного файла
    
    Args:
        file: Загруженный файл
        folder: Поддиректория для сохранения
    
    Returns:
        str: Путь к сохраненному файлу относительно MEDIA_ROOT
    """
    # Проверяем тип файла
    if file.content_type not in settings.ALLOWED_MEDIA_TYPES:
        raise ValueError("Неподдерживаемый тип файла")
        
    # Генерируем уникальное имя
    filename = generate_unique_filename(file.filename)
    
    # Создаем путь для сохранения
    save_path = get_media_path(folder) / filename
    
    # Сохраняем файл
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
        
    return f"{folder}/{filename}" 