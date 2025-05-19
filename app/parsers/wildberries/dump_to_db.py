from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from app.models.wb.shard_query import ShardQueryTable
from app.models.wb.trands import TrandsTable

from datetime import datetime
from app.core.app_logger import get_logger

logger = get_logger(__name__)

async def save_to_db(trands_data, category_data, session_maker):
    async with session_maker() as session:
        async with session.begin():
            try:
                # Объединяем данные категорий с основными данными
                for trand in trands_data:
                    category_info = next((
                        cat for cat in category_data 
                        if cat['id_trands'] == trand['id_src']
                    ), None)
                    
                    if category_info:
                        trand.update({
                            'category_ru': category_info['category_ru'],
                            'category_eng': category_info['category_eng'],
                            'podcat_1_ru': category_info['podcat_1_ru'],
                            'podcat_1_eng': category_info['podcat_1_eng'],
                            'podcat_2_ru': category_info['podcat_2_ru'],
                            'podcat_2_eng': category_info['podcat_2_eng'],
                            'podcat_3_ru': category_info['podcat_3_ru'],
                            'podcat_3_eng': category_info['podcat_3_eng'],
                            'podcat_4_ru': category_info['podcat_4_ru'],
                            'podcat_4_eng': category_info['podcat_4_eng'],
                            'podcat_5_ru': category_info['podcat_5_ru'],
                            'podcat_5_eng': category_info['podcat_5_eng'],
                        })
                
                # Сохраняем все в основную таблицу
                if trands_data:
                    trands_data_ignore = insert(TrandsTable).values(trands_data).prefix_with("IGNORE")
                    await session.execute(trands_data_ignore)
                logger.info("All data saved successfully.")
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