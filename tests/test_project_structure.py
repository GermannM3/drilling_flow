"""
Тесты структуры проекта
"""
import os
from pathlib import Path

def test_project_structure():
    """Проверяет наличие всех необходимых файлов и папок"""
    root = Path(__file__).parent.parent
    
    # Проверяем основные директории
    required_dirs = [
        "app",
        "app/api",
        "app/bot",
        "app/core",
        "app/db",
        "app/db/models",
        "app/routers",
        "app/services",
        "app/static",
        "app/static/webapp",
        "tests",
    ]
    
    for dir_path in required_dirs:
        assert (root / dir_path).is_dir(), f"Директория {dir_path} не найдена"
    
    # Проверяем критически важные файлы
    required_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-test.txt",
        "pytest.ini",
        ".env",
        ".gitignore",
        "app/main.py",
        "app/core/config.py",
        "app/core/application.py",
        "app/db/base.py",
        "app/bot/bot.py",
        "app/static/webapp/style.css",
    ]
    
    for file_path in required_files:
        assert (root / file_path).is_file(), f"Файл {file_path} не найден"
    
    # Проверяем содержимое .env
    env_vars = [
        "DATABASE_URL",
        "TELEGRAM_TOKEN",
        "YANDEX_API_KEY",
        "SECRET_KEY",
    ]
    
    env_path = root / ".env"
    if env_path.exists():
        env_content = env_path.read_text()
        for var in env_vars:
            assert var in env_content, f"Переменная {var} не найдена в .env"

def test_python_files():
    """Проверяет все Python файлы на наличие синтаксических ошибок"""
    root = Path(__file__).parent.parent
    
    for path in root.rglob("*.py"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                compile(f.read(), path, "exec")
        except Exception as e:
            raise AssertionError(f"Ошибка в файле {path}: {str(e)}")

def test_static_files():
    """Проверяет статические файлы"""
    root = Path(__file__).parent.parent
    static_dir = root / "app" / "static" / "webapp"
    
    # Проверяем наличие CSS файлов
    css_files = list(static_dir.glob("*.css"))
    assert len(css_files) > 0, "CSS файлы не найдены"
    
    # Проверяем содержимое style.css
    style_css = static_dir / "style.css"
    assert style_css.exists(), "style.css не найден"
    content = style_css.read_text()
    assert "@import" in content, "Отсутствуют импорты в style.css" 