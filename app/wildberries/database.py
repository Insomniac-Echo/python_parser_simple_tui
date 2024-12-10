from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import IntegrityError
from app.wildberries.database_models import Base, TrandsTable, TrandsInfoTable, CategoryTrandsTable
from app.utils.app_logger import get_logger

logger = get_logger(__name__)

# Инициализация базы данных
async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully.")

async def save_to_db(trands_data, trands_info_data, category_data, session_maker):
    async with session_maker() as session:
        try:
            # Сохраняем trands
            if trands_data:
                session.bulk_insert_mappings(TrandsTable, trands_data)
                await session.commit()

            # Сохраняем trands_info
            if trands_info_data:
                session.bulk_insert_mappings(TrandsInfoTable, trands_info_data)
                await session.commit()

            # Сохраняем category_trands
            if category_data:
                session.bulk_insert_mappings(CategoryTrandsTable, category_data)
                await session.commit()

            logger.info("All data saved successfully.")
        except IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            await session.rollback()
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            await session.rollback()

def validate_foreign_keys(trands_data, trands_info_data, category_data):
    trands_ids = {trand["id_src"] for trand in trands_data}
    trands_info_data = [
        info for info in trands_info_data if info["id_trands"] in trands_ids
    ]
    category_data = [
        category for category in category_data if category["id_trands"] in trands_ids
    ]
    return trands_info_data, category_data


