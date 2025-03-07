from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker, registry
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.core.config import DATABASE_URL
from app.core.app_logger import get_logger

logger = get_logger(__name__)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
mapper_registry = registry()

# Основные функции в бд, вряд ли потребуется вмешательство, но лучше тоже посмотреть save_to_db
# Инициализация базы данных
async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)
    logger.info("Database initialized successfully.")
