import json
import asyncio

from curl_cffi.requests import AsyncSession
from pydantic import ValidationError
from curl_cffi import requests
from app.wildberries.entities import DataValidationError
from app.wildberries.data_validation import data_validation
from app.wildberries.data_processing import get_details_from_json
from app.utils.app_logger import get_logger

logger = get_logger(__name__)

#Переписать кривые exception, который я писал видимо из дурки
#Основная функция-обработчик парсера.
async def get_data_say_gex(url: str, session: AsyncSession, max_retries: int = 12):
    retries = 0
    while retries <= max_retries:
        try:
            response = await session.get(url, impersonate="chrome")
            if response.status_code == 200:
                try:
                    text = response.text
                    data = json.loads(text)
                    verify = await data_validation(data)
                    if verify is not None:
                        logger.info("Success data extraction.")
                        return await get_details_from_json(session, data)
                    else:
                        logger.error(f"Data validation failed. Retrying ({retries + 1}/{max_retries})...")
                        retries += 1
                        await asyncio.sleep(3)
                except json.JSONDecodeError:
                    logger.error("JSON decode error.")
                    retries += 1
                    await asyncio.sleep(3)
                except DataValidationError:
                    logger.error(f"Data validation error. Retrying ({retries + 1}/{max_retries})...")
                    retries += 1
                    await asyncio.sleep(3)
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded. Retrying in 3 seconds.")
                await asyncio.sleep(3)
                retries += 1
            else:
                logger.error(f"Request error, status code is {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            retries += 1
            await asyncio.sleep(3)

    logger.error("Max retries reached. Exiting.")
    return None


async def get_data_dict(url: str):    
    async with AsyncSession() as session:
        while True:    
            response = await session.get(url, impersonate="chrome")     
            if response.status_code == 200:
                try:
                    text = response.text
                    data = json.loads(text)
                    verify = await data_validation(data)
                    if verify is not None:
                        logger.info("Success data extraction.")
                        return await get_details_from_json(session, data)  
                    else:
                        raise DataValidationError()  
                except json.JSONDecodeError:
                    logger.error("JSON decode error.")
                except DataValidationError:
                    logger.error("Data validation error, restart in 3 seconds.")
                    await asyncio.sleep(3)
            else:
                logger.error(f"Request error, status code is {response.status_code}")


async def parse_shard_and_query(session: AsyncSession):
    url = "https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json"
    try:
        response = await session.get(url, impersonate="chrome")
        if response.status_code == 200:
            data = response.json()
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