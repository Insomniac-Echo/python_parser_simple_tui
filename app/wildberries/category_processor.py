from app.wildberries.parser_category import get_data_say_gex
from app.wildberries.database import save_to_db, validate_foreign_keys
from app.utils.app_logger import get_logger
from app.wildberries.dictionary import category_links
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
        for category, base_url in category_links.items():
            trands_data = []
            trands_info_data = []
            category_data = []
            product_data = []

            async for items in recursive_parse_category(category, base_url, session):
                for item in items:
                    trands_data.append({
                        "id_src": item["id_src"],
                        "rating": item["rating"],
                        "reviewRating": item["reviewRating"],
                        "feedbacks": item["feedbacks"],
                        "basic_price": item["basic_price"],
                        "product_price": item["product_price"],
                        "total_price": item["total_price"],
                        "count_sales": 0,
                        "on_stock": 0,
                    })

                    trands_info_data.append({
                        "id_trands": item["id_src"],
                        "name": item["name"],
                        "brand": item["brand"],
                        "cashback": item["cashback"],
                        "sale": item["sale"],
                        "link": item["link"],
                        "img_link": item["img_url"],
                    })

                    category_data.append({
                        "id_trands": item["id_src"],
                        "category_ru": item["category"]["name_1"],
                        "category_eng": item["category"]["name_1_eng"],
                        "category_id": 1,
                        "parent_id": 0,
                    })

                    product_data.append({
                        "id_src": item["id_src"],
                        "name": item["name"],
                        "cashback": item["cashback"],
                        "sale": item["sale"],
                        "brand": item["brand"],
                        "rating": item["rating"],
                        "supplier": item["supplier"],
                        "supplierRating": item["supplierRating"],
                        "feedbacks": item["feedbacks"],
                        "reviewRating": item["reviewRating"],
                        "promoTextCard": item["promoTextCard"],
                        "basic_price": item["basic_price"],
                        "product_price": item["product_price"],
                        "total_price": item["total_price"],
                        "logistics_price": item["logistics_price"],
                        "return_price": item["return_price"],
                        "link": item["link"],
                        "img_link": item["img_url"],
                        "description": item["description"],
                        "category_ru": item["category"]["name_1"],
                        "category_eng": item["category"]["name_1_eng"],
                        "category_id": 1,
                        "parent_id": 0,
                    })

            trands_info_data, category_data = validate_foreign_keys(trands_data, trands_info_data, category_data)

            logger.info(f"Saving data for category: {category}")
            await save_to_db(trands_data, trands_info_data, category_data, product_data, session_maker)

    logger.info("All categories processed and saved.")