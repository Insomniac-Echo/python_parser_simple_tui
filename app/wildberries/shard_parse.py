import json

from curl_cffi.requests import AsyncSession
from curl_cffi import requests

from app.utils.app_logger import get_logger
from app.wildberries.database import dump_shard_query

logger = get_logger(__name__)
shard_query_seo = []
parsed_categories = set()  #храним уникальные ключи

def extract_items(items):
    for item in items:
        if "shard" in item and "query" in item and "name" in item:
            category_key = (item["shard"], item["query"], item["name"])  #уникальный ключ для каждой категории
            if category_key not in parsed_categories:  #проверяем парсили ли мы это уже или нет
                shard_query_seo.append({
                    "shard": item["shard"],
                    "query": item["query"],
                    "name": item.get("name", "")
                })
                parsed_categories.add(category_key)

                logger.debug(f"Extracted category: {item['name']} (shard: {item['shard']}, query: {item['query']})")
            else:
                logger.debug(f"Skipping duplicate category: {item['name']} (shard: {item['shard']}, query: {item['query']})")
        else:
            logger.warning(f"Missing required fields in item: {item}")

        if "childs" in item:
            logger.debug(f"Processing child categories for: {item.get('name', 'Unnamed Category')}")
            extract_items(item["childs"])

async def parse_shard_and_query(session: AsyncSession):
    
    url = "https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json"
    
    try:
        response = await session.get(url, impersonate="chrome")
        if response.status_code == 200:
            data = response.json()
            extract_items(data)
            logger.info(f"Successfully extracted {len(shard_query_seo)} unique shard and query pairs.")
            return shard_query_seo
        else:
            logger.error(f"Failed to fetch data from {url}. Status code: {response.status_code}")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error while parsing response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while parsing shard and query: {e}")
        return None

async def parse_dump_shard(session_maker):
    async with requests.AsyncSession() as session:
        data = await parse_shard_and_query(session)
        if not data:
            logger.error("No shard and query pairs found.")
            return
        
        logger.info("Saving data...")
        await dump_shard_query(data, session_maker)
        logger.info("Saving data complete...")
