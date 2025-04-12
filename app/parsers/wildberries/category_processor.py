import asyncio
from app.parsers.wildberries.parser_category import get_data_say_gex, parse_shard_and_query
from app.parsers.wildberries.dump_to_db import save_to_db
from app.core.app_logger import get_logger
from curl_cffi import requests
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wb.shard_query import ShardQueryTable
from sqlalchemy.future import select
from app.parsers.wildberries.data_processing import get_category
from app.api.routes.wb import task_storage

logger = get_logger(__name__)

category_cache = {}
category_cache_lock = asyncio.Lock()

async def recursive_parse_category(category, base_url, session):
    page = 1
    while True:
        url = f"{base_url}&page={page}"
        logger.info(f"Processing category: {category}, page: {page}, URL: {url}")

        try:
            response = await get_data_say_gex(url, session)
            if response is None:
                logger.error(f"Failed to fetch data for category {category}, page {page}. Stopping pagination.")
                break

            if isinstance(response, list):
                items = response
            elif isinstance(response, dict):
                items = response.get("data", [])
            else:
                logger.error(f"Unexpected response format for category {category}: {type(response)}")
                break

            if not items:
                logger.warning(f"No items found for category: {category}, page: {page}. Stopping pagination.")
                break

            yield items

        except Exception as e:
            logger.error(f"Error processing category {category}, page {page}: {e}")
            break

        page += 1

async def process_and_save(session_maker):
    async with requests.AsyncSession() as session:
        shard_query = await parse_shard_and_query(session)
        if not shard_query:
            logger.error("No shard and query pairs found.")
            return

        category_cache = {} #словарь для кэшеирования категорий

        for pair in shard_query:
            trands_data = []
            category_data = []

            base_url = f"https://catalog.wb.ru/catalog/{pair['shard']}/v2/catalog?ab_testing=false&appType=1&{pair['query']}&curr=rub&dest=-284542&hide_dtype=10&lang=ru&sort=popular&spp=30"

            async for items in recursive_parse_category(pair['name'], base_url, session):
                #функция для уменьшения количества запросов на поулчение категории товара
                if pair['query'] not in category_cache:
                    logger.info(f"Fetching category data for category: {pair['name']}")
                    if items:
                        first_item = items[0]
                        subject_id = first_item.get("subjectId")
                        kind_id = first_item.get("kindId")
                        brand_id = first_item.get("brandId")
                        category = await get_category(
                            session,
                            first_item["id_src"],
                            brand_id,
                            subject_id,
                            kind_id
                        )
                        
                        if category:
                            category_cache[pair['query']] = category # кэшируем данные
                        else:
                            logger.warning(f"Failed to fetch category data for category: {pair['name']}")
                            category_cache[pair['query']] = None
                    else:
                        logger.warning(f"No items found for category: {pair['name']}")
                        category_cache[pair['query']] = None

                category = category_cache.get(pair['query'])

                for item in items:
                    trands_data.append({
                        "id_src": item["id_src"],
                        "name": item["name"],
                        "rating": item["rating"],
                        "reviewRating": item["reviewRating"],
                        "feedbacks": item["feedbacks"],
                        "basic_price": item["basic_price"],
                        "product_price": item["product_price"],
                        "total_price": item["total_price"],
                        "count_sales": item["count_sales"],
                        "on_stock": item["on_stock"],
                        "link": item["link"],
                        "img_link": item["img_url"],
                    })

                    if category:
                        category_ru = category.get("name_1", "")
                        logger.info(f"category_ru: {category_ru}")
                        category_eng = category.get("name_1_eng", "")
                        logger.info(f"category_eng: {category_eng}")
                        podcats_ru = [category.get(f"name_{level}", "") for level in range(2, 7)] #от 2 до 7 потому что 1 это основная категория,остальное подкатегории
                        logger.info(f"podcats_ru: {podcats_ru}")
                        podcats_eng = [category.get(f"name_{level}_eng", "") for level in range(2, 7)]
                        logger.info(f"podcats_eng: {podcats_eng}")

                        category_row = {
                            "id_trands": item["id_src"],
                            "category_ru": category_ru,
                            "category_eng": category_eng,
                            "podcat_1_ru": podcats_ru[0] if len(podcats_ru) > 0 else None,
                            "podcat_1_eng": podcats_eng[0] if len(podcats_eng) > 0 else None,
                            "podcat_2_ru": podcats_ru[1] if len(podcats_ru) > 1 else None,
                            "podcat_2_eng": podcats_eng[1] if len(podcats_eng) > 1 else None,
                            "podcat_3_ru": podcats_ru[2] if len(podcats_ru) > 2 else None,
                            "podcat_3_eng": podcats_eng[2] if len(podcats_eng) > 2 else None,
                            "podcat_4_ru": podcats_ru[3] if len(podcats_ru) > 3 else None,
                            "podcat_4_eng": podcats_eng[3] if len(podcats_eng) > 3 else None,
                            "podcat_5_ru": podcats_ru[4] if len(podcats_ru) > 4 else None,
                            "podcat_5_eng": podcats_eng[4] if len(podcats_eng) > 4 else None,
                        }
                        category_data.append(category_row)

            logger.info(f"Saving data for shard: {pair['shard']}")
            await save_to_db(trands_data, category_data, session_maker)
    logger.info("All categories processed and saved.")


#тест
async def worker(worker_id, task_queue, session_maker):
    async with requests.AsyncSession() as session:
        while True:
            pair = await task_queue.get()
            if pair is None:  # Завершение работы воркера
                logger.info(f"Worker {worker_id} shutting down.")
                break

            logger.info(f"Worker {worker_id} processing shard: {pair['shard']}, query: {pair['query']}")
            try:
                trands_data = []
                category_data = []
                base_url = f"https://catalog.wb.ru/catalog/{pair['shard']}/v2/catalog?ab_testing=false&appType=1&{pair['query']}&curr=rub&dest=-284542&hide_dtype=10&lang=ru&sort=popular&spp=30"

                async for items in recursive_parse_category(pair['name'], base_url, session):
                    async with category_cache_lock:
                        if pair['query'] not in category_cache:
                            logger.info(f"Fetching category data for category: {pair['name']}")
                            if items:
                                first_item = items[0]
                                subject_id = first_item.get("subjectId")
                                kind_id = first_item.get("kindId")
                                brand_id = first_item.get("brandId")
                                category = await get_category(
                                    session,
                                    first_item["id_src"],
                                    brand_id,
                                    subject_id,
                                    kind_id
                                )

                                if category:
                                    category_cache[pair['query']] = category  # кэшируем данные
                                    logger.info(f"{category_cache}")
                                else:
                                    logger.warning(f"Failed to fetch category data for category: {pair['name']}")
                                    category_cache[pair['query']] = None

                    for item in items:
                        trands_data.append({
                            "id_src": item["id_src"],
                            "name": item["name"],
                            "rating": item["rating"],
                            "reviewRating": item["reviewRating"],
                            "feedbacks": item["feedbacks"],
                            "basic_price": item["basic_price"],
                            "product_price": item["product_price"],
                            "total_price": item["total_price"],
                            "count_sales": item["count_sales"],
                            "on_stock": item["on_stock"],
                            "link": item["link"],
                            "img_link": item["img_url"],
                        })

                        if category:
                            category_row = {
                                "id_trands": item["id_src"],
                                "category_ru": category.get("name_1", ""),
                                "category_eng": category.get("name_1_eng", ""),
                                "podcat_1_ru": category.get("name_2", ""),
                                "podcat_1_eng": category.get("name_2_eng", ""),
                                "podcat_2_ru": category.get("name_3_eng", ""),
                                "podcat_2_eng": category.get("name_3", ""),
                                "podcat_3_ru": category.get("name_4", ""),
                                "podcat_3_eng": category.get("name_4_eng", ""),
                                "podcat_4_ru": category.get("name_5", ""),
                                "podcat_4_eng": category.get("name_5_eng", ""),
                                "podcat_5_ru": category.get("name_6", ""),
                                "podcat_5_eng": category.get("name_6_eng", ""),
                            }
                            category_data.append(category_row)

                await save_to_db(trands_data, category_data, session_maker)
                logger.info(f"Worker {worker_id} finished processing shard: {pair['shard']}")
            except Exception as e:
                logger.error(f"Worker {worker_id} encountered an error: {e}")
            finally:
                task_queue.task_done()

async def process_with_workers(task_id, session_maker, num_workers=16):
    task_queue = asyncio.Queue()

    # Получение данных из таблицы shard_query
    async with session_maker() as db_session:
        result = await db_session.execute(select(ShardQueryTable))
        shard_queries = result.scalars().all()

    # Добавление задач в очередь
    for shard_query in shard_queries:
        task_queue.put_nowait({
            "shard": shard_query.shard,
            "query": shard_query.query,
            "name": shard_query.name,
        })

    # Создание воркеров
    workers = [
        asyncio.create_task(worker(worker_id, task_queue, session_maker))
        for worker_id in range(num_workers)
    ]

    # Ожидание завершения всех задач
    await task_queue.join()

    # Завершение работы воркеров
    for _ in range(num_workers):
        task_queue.put_nowait(None)

    await asyncio.gather(*workers)
    logger.info("All workers have completed their tasks.")
    
    # Удаление задачи из хранилища
    if task_id:
        task_storage.pop(task_id, None)
        logger.info(f"Task {task_id} removed from task_storage.")