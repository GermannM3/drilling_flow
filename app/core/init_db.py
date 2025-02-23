from app.core.database import Base, engine

def init_db():
    """Инициализация базы данных"""
    Base.metadata.create_all(bind=engine) 