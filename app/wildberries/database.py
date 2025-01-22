from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from app.wildberries.database_models import Base, TrandsTable, CategoryTrandsTable
from app.utils.app_logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

# Основные функции в бд, вряд ли потребуется вмешательство, но лучше тоже посмотреть save_to_db
# Инициализация базы данных
async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully.")

async def save_to_db(trands_data, category_data, session_maker):
    async with session_maker() as session:
        async with session.begin():
            try:
                # Сохраняем время
                current_timestamp = datetime.now()
                for trand in trands_data:
                    trand["date_of"] = current_timestamp

                # Сохраняем trands
                if trands_data:
                    trands_data_ignore = insert(TrandsTable).values(trands_data).prefix_with("IGNORE")
                    await session.execute(trands_data_ignore)

                # Сохраняем category_trands
                if category_data:
                    category_data_ignore = insert(CategoryTrandsTable).values(category_data).prefix_with("IGNORE")
                    await session.execute(category_data_ignore)

                logger.info("All data saved successfully.")
            except IntegrityError as e:
                logger.error(f"Database integrity error: {e}")
                await session.rollback()
            except Exception as e:
                logger.error(f"Error saving to database: {e}")
                await session.rollback()

def validate_foreign_keys(trands_data, category_data):
    trands_ids = {trand["id_src"] for trand in trands_data}

    category_data = [
        category for category in category_data if category["id_trands"] in trands_ids
    ]
    return category_data