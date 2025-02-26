"""
Database configuration and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
    pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
    echo=settings.DEBUG
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# Export all
__all__ = ["Base", "engine", "async_session_maker", "get_async_session"] 