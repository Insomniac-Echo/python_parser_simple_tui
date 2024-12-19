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
                logger.error("Data validation error, restarting in 3 seconds.")
                await asyncio.sleep(3)
        elif response.status_code == 429:
            # рейт лимит, тяжело
            if retries < max_retries:
                logger.warning("Rate limit exceeded. Retrying in 2 seconds.")
                await asyncio.sleep(2)
                retries += 1
            else:
                logger.error("Max retries reached for 429 status code. Stopping.")
                return None
        else:
            logger.error(f"Request error, status code is {response.status_code}")
            return None

    logger.error("Max retries reached. Exiting.")
    return None