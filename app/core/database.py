from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.core.config import DATABASE_URL
from app.core.app_logger import get_logger
from app.models.wb.base import Base



logger = get_logger(__name__)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=30,  # Размер пула
    max_overflow=20,  # Дополнительные соединения при нагрузке
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


# Основные функции в бд, вряд ли потребуется вмешательство, но лучше тоже посмотреть save_to_db
# Инициализация базы данных
async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Ключи")
        logger.info(Base.metadata.tables.keys())
    logger.info("Database initialized successfully.")
