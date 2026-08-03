"""
Database Connection Setup
==========================
PostgreSQL: SQLAlchemy async engine + session factory
MongoDB:    Motor async client

TODO:
  - Call init_db() inside FastAPI lifespan startup
  - Add get_db() FastAPI dependency for PostgreSQL sessions
  - Add get_mongo_collection() helper for MongoDB
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import motor.motor_asyncio

from app.core.config import settings

# --- PostgreSQL ---
engine = create_async_engine(settings.POSTGRES_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all PostgreSQL models."""
    pass


async def get_db():
    """FastAPI dependency: yields an async SQLAlchemy session."""
    async with AsyncSessionLocal() as session:
        yield session


# --- MongoDB ---
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
mongo_db = mongo_client[settings.MONGO_DB_NAME]
