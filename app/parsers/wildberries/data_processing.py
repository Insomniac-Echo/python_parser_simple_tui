import json
import os
from curl_cffi import requests
from curl_cffi.requests import AsyncSession
from pydantic import ValidationError
import asyncio
from app.core.app_logger import get_logger
from app.parsers.wildberries.utils import remove_emojis, get_basket_number, get_review_basket_number

from app.core.config import get_sales_token, LIKESTATS_EMAIL, LIKESTATS_PASS

logger = get_logger(__name__)

async def get_product_info(basket_number, id):
    url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:4]}/part{str(id)[:6]}/{str(id)}/info/ru/card.json"
    try:
        response = requests.get(url, impersonate="chrome")
        response.raise_for_status()
        product_data = response.json()

        size_on_model = None
        model_parameters = None
        for option in product_data.get('options', []):
            if option.get('name') == 'Размер на модели':
                size_on_model = option.get('value')
            elif option.get('name') == 'Параметры модели на фото (ОГ-ОТ-ОБ)':
                model_parameters = option.get('value')

        sizes_table_data = product_data.get('sizes_table')
        processed_sizes = []

        if sizes_table_data and 'details_props' in sizes_table_data and 'values' in sizes_table_data:
            details_props = sizes_table_data['details_props']
            for size_value in sizes_table_data['values']:
                size_details = {
                    "tech_size": size_value.get("tech_size"),
                    "chrt_id": size_value.get("chrt_id")
                }
                details = size_value.get("details", [])
                for i, prop in enumerate(details_props):
                    if i < len(details):
                        size_details[prop] = details[i]
                processed_sizes.append(size_details)

        return {
            "size_on_model": size_on_model,
            "model_parameters": model_parameters,
            "sizes_table": processed_sizes
        }
    except Exception as e:
        logger.error(f"Error fetching product info for ID {id}: {e}")
        return None
    

async def get_product_reviews(session, root):
    urls_to_try = [
        f"https://feedbacks2.wb.ru/feedbacks/v2/{root}",
        f"https://feedbacks1.wb.ru/feedbacks/v1/{root}"
    ]

    processed_reviews_data = {
        'matching_size_percentages': None,
        'reviews': []
    }

    for url in urls_to_try:
        logger.info(f"Attempting to fetch reviews from: {url}")
        try:
            response = await session.get(url)
            response.raise_for_status()
            reviews_data = response.json()

            if reviews_data.get("feedbackCount", 0) == 0 and not reviews_data.get("feedbacks"):
                 logger.info(f"No feedback data in response from {url}. Trying next URL if available.")
                 continue

            logger.info(f"Successfully fetched reviews from: {url}")

            if reviews_data and isinstance(reviews_data, dict):
                processed_reviews_data['matching_size_percentages'] = reviews_data.get('matchingSizePercentages')

                feedbacks = reviews_data.get('feedbacks')
                if feedbacks and isinstance(feedbacks, list):
                    for feedback in feedbacks:
                        review_size = feedback.get('size')
                        photo_ids = feedback.get('photo', [])

                        review_photo_urls = []
                        if photo_ids:
                            review_photo_urls = [await get_review_image_url(get_review_basket_number(pid), pid) for pid in photo_ids]

                        processed_reviews_data['reviews'].append({
                            'matching_size': feedback.get('matchingSize'),
                            'size': review_size,
                            'photo_ids': photo_ids,
                            'photo_urls': review_photo_urls,
                        })

            return processed_reviews_data

        except requests.errors.RequestsError as e:
            logger.warning(f"Error fetching reviews from {url}: {e}. Trying next URL if available.")
        except Exception as e:
            logger.warning(f"Error processing reviews from {url}: {e}. Trying next URL if available.")

    logger.error(f"Failed to fetch valid reviews data from all attempts for root {root}")
    return None




#Функция для получения словаря категорий, требует доработки.
async def get_category(session, id, brandid, subjectid, kindid, max_retries=5):
    url = f"https://www.wildberries.ru/webapi/product/{id}/data?subject={subjectid}&kind={kindid}&brand={brandid}"
    retries = 0
    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'deviceid': 'site_99d04ef106944d24bee830f7f6e65aee',
        'dnt': '1',
        'priority': 'u=1, i',
        'referer': f'https://www.wildberries.ru/catalog/{id}/detail.aspx',
        'sec-ch-ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-spa-version': '12.2.4',
}

    while retries < max_retries:
        try:
            response = await session.get(url, impersonate="chrome", headers=headers, timeout=55)
            if response.status_code == 404:
                logger.warning(f"Category not found for product ID {id}. Status code: {response.status_code}")
                return None
            elif response.status_code != 200:
                logger.error(f"Status code other than 200 or 404. Local or Server error? Status code: {response.status_code}")
                return None

            category = response.json()

            if "value" in category:
                site_path = category["value"].get("data", {}).get("sitePath", [])
                parsed_data = {}
                for i, item in enumerate(site_path[:-1], start=1):
                    key = f"name_{i}"
                    key_eng = f"name_{i}_eng"
                    name = item.get("name")
                    page_url = item.get("pageUrl")
                    if name and page_url:
                        parsed_data[key] = name
                        parsed_data[key_eng] = page_url.split('/')[-1]
                return parsed_data
            else:
                logger.warning(f"Category not found for product ID {id}.")
                return None
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            retries += 1
            logger.error(f"Error occurred while fetching category for product ID {id}: {e}. Retrying ({retries}/{max_retries}).")
            await asyncio.sleep(10)

    logger.error(f"Max retries reached for product ID {id}.")
    return None

async def get_review_image_url(basket_review_number, id):
    img_url = f"https://feedback{basket_review_number}.wbbasket.ru/vol{str(id)[:4]}/part{str(id)[:6]}/{str(id)}/photos/fs.webp"
    return img_url

#Функция для получения ссылки на изображение карточки товара.
async def get_image_url(id, basket_number):
    if basket_number in ["01"]:
        img_url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:2]}/part{str(id)[:4]}/{str(id)}/images/big/1.webp"
    elif basket_number in ["02", "03", "04", "05"]:
        img_url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:3]}/part{str(id)[:5]}/{str(id)}/images/big/1.webp"
    else:
        img_url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:4]}/part{str(id)[:6]}/{str(id)}/images/big/1.webp"

    return img_url

#Функция для получения количества продаж, стороннее апи
async def get_sales_quantity(session: AsyncSession, product_id: int, max_retries: int = 2):

    retries = 0
    while retries < max_retries:
        url = f"https://api.likestats.io/extension/product/{product_id}/quantity"

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Origin': 'https://www.wildberries.ru',
            'Referer': f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'authorization': f'Bearer {get_sales_token()}',
            'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="130"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        }

        try:
            response = await session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                sizes_data = data.get("sizes", [])
                total_sales = sum(item.get("sales", 0) for item in sizes_data)
                return total_sales, response.status_code
            elif response.status_code == 401:
                logger.error("Token expired. Waiting for a new token.")
                new_token = await get_new_token(session)
                if not new_token:
                    logger.error("Failed to refresh token")
                    return 0, response.status_code
                retries += 1
                continue
            else:
                logger.error(f"Failed to fetch sales data for product ID {product_id}. Status code: {response.status_code}")
                return 0, response.status_code
        except Exception as e:
            logger.error(f"Error fetching sales data for product ID {product_id}: {e}")
            return 0, 500

    logger.error(f"Max retries reached for product ID {product_id}. Exiting.")
    return 0, 429


async def get_new_token(session: AsyncSession):
    url = "https://api.likestats.io/user/login"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'https://my.likestats.io',
        'Referer': 'https://my.likestats.io/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }
    json_data = {
        'email': f'{LIKESTATS_EMAIL}',
        'password': f'{LIKESTATS_PASS}',
        'remember': False,
        'redirect': '</>',
        'oauth_token': None,
    }

    try:
        response = await session.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        token_data = response.json()
        new_token = token_data.get("token")
        if new_token:
            os.environ["SALES_API_TOKEN"] = new_token
            session.headers.update({'authorization': f'Bearer {new_token}'})
            logger.info("New token acquired successfully")
            logger.info(f"New token: {get_sales_token()}")
            return new_token
        logger.error("Token not found in response")
        return None
    except Exception as e:
        logger.error(f"Failed to fetch new token: {e}")
        return None

#Функция для пост-обработки JSON данных о товарах,
#возможно, в будущем будет deprecated из-за внедрения pydantic
#(слияние с основной функцией парсера)
#Нужна доработка последних полей начиная с img_url до categories:
#доработка кода или же модели
async def get_details_from_json(session, response):
    data_list = []
    
    for data in response['data']['products']:
        try:
            basket_number = get_basket_number(data.get('id'))
            try:
                img_url = await get_image_url(data.get('id'), basket_number)
            except Exception as e:
                logger.warning(f"Failed to fetch image URL for product {data.get('id')}: {e}")
                img_url = "" 
            #sales_quantity, status_code = await get_sales_quantity(session, data.get('id'))
            
            product_info_task = get_product_info(basket_number, data.get('id'))
            product_reviews_task = get_product_reviews(session, data.get('root'))
            
            product_info, product_reviews = await asyncio.gather(
                product_info_task, 
                product_reviews_task,
                return_exceptions=True
            )
            
            if isinstance(product_info, Exception):
                logger.error(f"Product info fetch failed: {product_info}")
                product_info = {}
                
            if isinstance(product_reviews, Exception):
                logger.error(f"Product reviews fetch failed: {product_reviews}")
                product_reviews = {}

            product_properties = {
                'id_src': data.get('id'),
                'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/detail.aspx?targetUrl=BP',
                'img_link': img_url,
                'subjectId': data.get('subjectId'),
                'kindId': data.get('kindId'),
                'brandId': data.get('brandId'), 
                'size_on_model': product_info.get('size_on_model'),
                'model_parameters': product_info.get('model_parameters'),
                'sizes_table': product_info.get('sizes_table', {}),
                'reviews_data': product_reviews or {}
            }
            data_list.append(product_properties)
            
        except ValidationError as e:
            logger.error(f"Validation error for product {data.get('id')}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing product {data.get('id')}: {e}")
    
    logger.info("Parse Wildberries operation successful. Sending data.")
    return data_list