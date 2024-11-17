import json

from curl_cffi import requests
from curl_cffi.requests import AsyncSession
from pydantic import ValidationError

from app.utils.app_logger import get_logger
from app.wildberries.utils import remove_emojis, get_basket_number
from app.models import Product

logger = get_logger(__name__)

#Функция для получения данные в поле description товара.
async def get_description(session, id, basket_number):
    if basket_number in ["01"]:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:2]}/part{str(id)[:4]}/{str(id)}/info/ru/card.json"
    elif basket_number in ["02", "03", "04", "05"]:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:3]}/part{str(id)[:5]}/{str(id)}/info/ru/card.json"
    else:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:4]}/part{str(id)[:6]}/{str(id)}/info/ru/card.json"

    try:
        response = await session.get(url, impersonate="chrome")
        if response.status_code != 200:
            logger.error("Status code other than 200. Local or Server error?")
            return None

        desc = response.json()   
        if "description" in desc:
            return desc["description"]
        else:
            logger.warning("Description not found.")
            return None
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logger.error(f"Error occurred: {e}")
        return None
        
#Функция для получения словаря категорий, требует доработки.
async def get_category(session, id, brandid, subjectid, kindid):
    url = f"https://www.wildberries.ru/webapi/product/{id}/data?subject={subjectid}&kind={kindid}&brand={brandid}"

    try:
        response = await session.get(url, impersonate="chrome")
        if response.status_code != 200:
            logger.error("Status code other than 200. Local or Server error?")
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
            logger.warning("Category not found.")
            return None
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logger.error(f"Error occurred: {e}")
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

#Функция для пост-обработки JSON данных о товарах,
#возможно, в будущем будет deprecated из-за внедрения pydantic
#(слияние с основной функцией парсера)
async def get_details_from_json(session, response):
    logger.info("Formatting data.")
    data_list = []
    for data in response['data']['products']:
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
            'img_url': await get_image_url(session, data.get('id'), get_basket_number(data.get('id'))),
            'description': await get_description(session, data.get('id'), get_basket_number(data.get('id'))),
            'category': await get_category(session, data.get('id'), data.get('brandId'), data.get('subjectId'), data.get('kindId'))
        }

        try:
            product = Product(**product_properties)
            data_list.append(product)
        except ValidationError as e:
            logger.error(f"Validation error for product {data.get('id')}: {e}")

    logger.info("Parse Wildberries operation successful. Sending data.")
    return data_list