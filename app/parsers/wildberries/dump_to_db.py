from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from app.models.wb.shard_query import ShardQueryTable
from app.models.wb.trands import TrandsTable

from datetime import datetime
from app.core.app_logger import get_logger

logger = get_logger(__name__)
BATCH_SIZE = 100
async def save_to_db(trands_data, session_maker):
    async with session_maker() as session:
        async with session.begin():
            try:
                logger.info(f"Starting batch insert. Total items: {len(trands_data)}")

                # Разбиваем на пакеты
                for i in range(0, len(trands_data), BATCH_SIZE):
                    batch = trands_data[i:i + BATCH_SIZE]
                    trands_data_ignore = insert(TrandsTable).values(batch).prefix_with("IGNORE")
                    await session.execute(trands_data_ignore)
                    logger.debug(f"Inserted batch {i // BATCH_SIZE + 1} of size {len(batch)}")
            except IntegrityError as e:
                logger.error(f"Database integrity error: {e}")
                await session.rollback()
            except Exception as e:
                logger.error(f"Error saving to database: {e}")
                await session.rollback()


async def dump_shard_query(data, session_maker):
    async with session_maker() as session:
        async with session.begin():
            try:
                shard_query = [ShardQueryTable(**item) for item in data]
                session.add_all(shard_query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка при сохранении: {e}")