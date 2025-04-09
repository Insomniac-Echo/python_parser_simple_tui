import json
import os
from curl_cffi import requests
from curl_cffi.requests import AsyncSession
from pydantic import ValidationError
import asyncio
from app.core.app_logger import get_logger
from app.parsers.wildberries.utils import remove_emojis, get_basket_number

from app.core.config import get_sales_token, LIKESTATS_EMAIL, LIKESTATS_PASS

logger = get_logger(__name__)

#Функция для получения словаря категорий, требует доработки.
async def get_category(session, id, brandid, subjectid, kindid, max_retries=3):
    url = f"https://www.wildberries.ru/webapi/product/{id}/data?subject={subjectid}&kind={kindid}&brand={brandid}"
    retries = 0
    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'deviceid': 'site_99d04ef106944d24bee830f7f6e65aee',
        'dnt': '1',
        'priority': 'u=1, i',
        'referer': f"https://www.wildberries.ru/catalog/{id}/detail.aspx",
        'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-spa-version': '11.4.1',
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

#Функция для получения ссылки на изображение карточки товара.
async def get_image_url(session, id, basket_number):
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
    logger.info("Formatting data.")
    data_list = []
    for data in response['data']['products']:
        try:
            img_url = await get_image_url(session, data.get('id'), get_basket_number(data.get('id')))
            if img_url is None:
                logger.warning(f"Failed to fetch image URL for product ID {data.get('id')}. Proceeding without image URL.")
                img_url = ""

            sales_quantity, status_code = await get_sales_quantity(session, data.get('id'))

            if status_code == 401:
                raise Exception("Token expired. Please update the token.")

            on_stock = data.get('totalQuantity', 0)

            product_properties = {
                'id_src': data.get('id'),
                'name': data.get('name'),
                'cashback': data.get('feedbackPoints'),
                'sale': data.get('sale'),
                'brand': remove_emojis(data.get('brand')),
                'rating': data.get('rating'),
                'supplier': data.get('supplier'),
                'supplierRating': data.get('supplierRating'),
                'feedbacks': data.get('feedbacks'),
                'reviewRating': data.get('reviewRating'),
                'promoTextCard': data.get('promoTextCard'),
                'basic_price': data.get('sizes', [{}])[0].get('price', {}).get('basic') / 100,
                'product_price': data.get('sizes', [{}])[0].get('price', {}).get('product') / 100,
                'total_price': data.get('sizes', [{}])[0].get('price', {}).get('total') / 100,
                'logistics_price': data.get('sizes', [{}])[0].get('price', {}).get('logistics'),
                'return_price': data.get('sizes', [{}])[0].get('price', {}).get('return'),
                'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/detail.aspx?targetUrl=BP',
                'img_url': img_url,
                'subjectId': data.get('subjectId'),
                'kindId': data.get('kindId'),
                'brandId': data.get('brandId'), 
                'on_stock': on_stock,
                'count_sales': sales_quantity,
            }
            #product = Product(**product_properties)
            data_list.append(product_properties)
            

        except ValidationError as e:
            logger.error(f"Validation error for product {data.get('id')}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing product {data.get('id')}: {e}")

    logger.info("Parse Wildberries operation successful. Sending data.")
    return data_list