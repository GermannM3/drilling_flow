"""
Инициализация базы данных
"""
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.base import Base, import_models
from alembic.config import Config
from alembic import command
import sqlalchemy.exc

async def init_db():
    """Создание таблиц в базе данных"""
    engine = create_async_engine(settings.get_database_url, echo=True)
    
    # Импортируем модели для создания таблиц
    import_models()
    
    # Пробуем применить миграции
    # try:
    #     alembic_cfg = Config("alembic.ini")
    #     command.upgrade(alembic_cfg, "head")
    # except Exception as e:
    #     print(f"Migration error: {e}")
        
    # Если миграции не удались, пробуем создать таблицы напрямую
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except sqlalchemy.exc.ProgrammingError as e:
        if "already exists" not in str(e):
            raise
        print(f"Ignoring duplicate object error: {e}") 