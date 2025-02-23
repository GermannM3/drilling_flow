"""
Тесты конфигурации
"""
import pytest
from pydantic_settings import BaseSettings
from app.core.config import Settings

def test_settings_loading():
    """Тест загрузки настроек"""
    settings = Settings()
    assert isinstance(settings, BaseSettings)
    assert hasattr(settings, 'POSTGRES_SERVER')
    assert hasattr(settings, 'TELEGRAM_TOKEN')

def test_database_url_formation():
    """Тест формирования URL базы данных"""
    settings = Settings(
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="test",
        POSTGRES_PASSWORD="test",
        POSTGRES_DB="test_db",
        DATABASE_URL=None  # Убеждаемся, что URL будет сформирован
    )
    assert settings.get_database_url.startswith("postgresql+asyncpg://")

@pytest.mark.parametrize("workers", [1, 2, 4, 8])
def test_workers_validation(workers):
    """Тест валидации количества воркеров"""
    settings = Settings(WORKERS=workers)
    assert settings.WORKERS > 0
    assert isinstance(settings.WORKERS, int) 