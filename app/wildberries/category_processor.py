from app.wildberries.parser_category import get_data_say_gex
from app.wildberries.database import save_to_db, validate_foreign_keys
from app.utils.app_logger import get_logger
from app.wildberries.dictionary import category_links


logger = get_logger(__name__)

async def process_and_save(session_maker):
    trands_data = []
    trands_info_data = []
    category_data = []

    for category, url in category_links.items():
        try:
            logger.info(f"Processing category: {category}")
            response = await get_data_say_gex(url)
            #logger.info(f"Response {response}")

            if isinstance(response, list):
                items = response
            elif isinstance(response, dict):
                items = response.get("data", [])
            else:
                logger.error(f"Unexpected response format for category {category}: {type(response)}")
                continue
        
            if not items:
                logger.warning(f"No items found for category: {category}")
                continue
            
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

        except Exception as e:
            logger.error(f"Error processing category {category}: {e}")

    logger.info(f"Trands Data: {trands_data}")
    logger.info(f"Trands Info Data: {trands_info_data}")
    logger.info(f"Category Data: {category_data}")

    trands_info_data, category_data = validate_foreign_keys(trands_data, trands_info_data, category_data)
    
    logger.info("Saving parsed data to database.")
    await save_to_db(trands_data, trands_info_data, category_data, session_maker)
