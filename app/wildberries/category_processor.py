from app.wildberries.parser_category import get_data_say_gex, parse_shard_and_query
from app.wildberries.database import save_to_db, validate_foreign_keys
from app.utils.app_logger import get_logger
#from app.wildberries.dictionary import category_links
from curl_cffi import requests

logger = get_logger(__name__)

# СРОЧНО доработать дроп данных в нужные таблицы в бд
async def recursive_parse_category(category, base_url, session):
    page = 1
    while True:
        url = f"{base_url}&page={page}"
        logger.info(f"Processing category: {category}, page: {page}")

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

        page += 1

async def process_and_save(session_maker):
    async with requests.AsyncSession() as session:
        shard_query = await parse_shard_and_query(session)
        if not shard_query:
            logger.error("No shard and query pairs found.")
            return

        for pair in shard_query:
            trands_data = []
            trands_info_data = []
            category_data = []

            base_url = f"https://catalog.wb.ru/catalog/{pair['shard']}/v2/catalog?ab_testing=false&appType=1&{pair['query']}&curr=rub&dest=-284542&hide_dtype=10&lang=ru&sort=popular&spp=30"

            async for items in recursive_parse_category(pair['name'], base_url, session):
                for item in items:
                    trands_data.append({
                        "id_src": item["id_src"],
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
                
                    #trands_info_data.append({
                    #    "id_trands": item["id_src"],
                    #    "name": item["name"],
                    #    "brand": item["brand"],
                    #    "cashback": item["cashback"],
                    #    "sale": item["sale"],
                    #    "link": item["link"],
                    #    "img_link": item["img_url"],
                    #})

                    category_data.append({
                        "id_trands": item["id_src"],
                        "category_ru": item["category"]["name_1"],
                        "category_eng": item["category"]["name_1_eng"],
                        "category_sub": item["category"]["name_2"],
                        "category_sub_sub": item["category"]["name_3"],
                        "parent_id": 0,
                    })

            trands_info_data, category_data = validate_foreign_keys(trands_data, trands_info_data, category_data)

            logger.info(f"Saving data for shard: {pair['shard']}")
            await save_to_db(trands_data, trands_info_data, category_data, session_maker)

    logger.info("All categories processed and saved.")