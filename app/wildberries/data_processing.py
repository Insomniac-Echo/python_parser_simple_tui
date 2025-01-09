import json

from curl_cffi import requests
from curl_cffi.requests import AsyncSession
from pydantic import ValidationError
import asyncio
from app.utils.app_logger import get_logger
from app.wildberries.utils import remove_emojis, get_basket_number
from app.models import Product

logger = get_logger(__name__)

#Функция для получения данные в поле description товара.
async def get_description(session, id, basket_number, name):
    if basket_number in ["01"]:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:2]}/part{str(id)[:4]}/{str(id)}/info/ru/card.json"
    elif basket_number in ["02", "03", "04", "05"]:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:3]}/part{str(id)[:5]}/{str(id)}/info/ru/card.json"
    else:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:4]}/part{str(id)[:6]}/{str(id)}/info/ru/card.json"

    try:
        response = await session.get(url, impersonate="chrome")
        if response.status_code != 200:
            logger.error(f"Status code other than 200. Local or Server error? Status code: {response.status_code}")
            return None

        desc = response.json()   
        if "description" in desc:
            return desc["description"]
        else:
            logger.warning(f"Description not found for {name}")
            return None
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logger.error(f"Error occurred: {e}")
        return None
        
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
async def get_sales_quantity(session: AsyncSession, product_id: int):

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
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'authorization': 'Bearer OIk0McAqJJTMeLQLNdW71XMiVptVO3nd',
    'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    }

    try:
        response = await session.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()

            sizes_data = data.get("sizes", [])

            total_sales = sum(item.get("sales", 0) for item in sizes_data)
            return total_sales
        else:
            logger.error(f"Failed to fetch sales data for product ID {product_id}. Status code: {response.status_code}")
            return 0
    except Exception as e:
        logger.error(f"Error fetching sales data for product ID {product_id}: {e}")
        return 0


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
            category = await get_category(
                session,
                data.get('id'),
                data.get('brandId'),
                data.get('subjectId'),
                data.get('kindId')
            )
            if category is None:
                logger.warning(f"Failed to fetch category for product ID {data.get('id')}. Proceeding with default category values.")
                category = {
                    "name_1": "Unknown Category",
                    "name_1_eng": "unknown_category"
                }

            img_url = await get_image_url(session, data.get('id'), get_basket_number(data.get('id')))
            if img_url is None:
                logger.warning(f"Failed to fetch image URL for product ID {data.get('id')}. Proceeding without image URL.")
                img_url = ""

            description = await get_description(
                session,
                data.get('id'),
                get_basket_number(data.get('id')),
                data.get('name')
            )
            if description is None:
                logger.warning(f"Failed to fetch description for product ID {data.get('id')}. Proceeding without description.")
                description = ""
            
            sales_quantity = await get_sales_quantity(session, data.get('id'))

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
                'description': description,
                'category': category,
                'on_stock': on_stock,
                'count_sales': sales_quantity,
            }
            
            product = Product(**product_properties)
            data_list.append(product.model_dump())
        except ValidationError as e:
            logger.error(f"Validation error for product {data.get('id')}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing product {data.get('id')}: {e}")

    logger.info("Parse Wildberries operation successful. Sending data.")
    return data_list