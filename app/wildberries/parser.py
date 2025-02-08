import json
import asyncio

from curl_cffi.requests import AsyncSession
from pydantic import ValidationError

from app.wildberries.entities import DataValidationError
from app.wildberries.data_validation import data_validation
from app.wildberries.data_processing import get_details_from_json
from app.utils.app_logger import get_logger

logger = get_logger(__name__)

#Переписать кривые exception, который я писал видимо из дурки
#Основная функция-обработчик парсера.
async def get_data(query):    
    url = fr'https://search.wb.ru/exactmatch/ru/common/v7/search?ab_testid=rerank_ksort_promo&appType=1&curr=rub&dest=-284542&query={query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
    
    async with AsyncSession() as session:
        while True:    
            await asyncio.sleep(60)
            response = await session.get(url, impersonate="chrome")     
            if response.status_code == 200:
                try:
                    text = response.text
                    data = json.loads(text)
                    verify = await data_validation(data)
                    if verify is not None:
                        logger.info("Success data extraction.")
                        logger.info(f"Задача была выполнена, отправили данные по запросу: {query}")
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
