import json
import asyncio
import aiohttp


from app.wildberries.entities import DataValidationError, InvalidContentJSON
from app.utils.app_logger import get_logger

logger = get_logger(__name__)

async def get_description(session, id, basket_number):
    if basket_number in ["01"]:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:2]}/part{str(id)[:4]}/{str(id)}/info/ru/card.json"
    elif basket_number in ["02", "03", "04", "05"]:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:3]}/part{str(id)[:5]}/{str(id)}/info/ru/card.json"
    else:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:4]}/part{str(id)[:6]}/{str(id)}/info/ru/card.json"

    async with session.get(url) as response:
        if response.status != 200:
            logger.warning("Status code other than 200. Local or Server error?")
            return None
        
        desc = await response.json()
        
        if "description" in desc:
            return desc["description"]
        else:
            logger.warning("Description not found.")
            return None

async def get_data(query):
    
    url = fr'https://search.wb.ru/exactmatch/ru/common/v7/search?ab_testid=rerank_ksort_promo&appType=1&curr=rub&dest=-284542&query={query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Origin': 'https://www.wildberries.ru',
        'Connection': 'keep-alive',
        'Referer': 'https://www.wildberries.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Priority': 'u=4'
    }
    
    async with aiohttp.ClientSession() as session:
        while True:    
            async with session.get(url, headers=headers) as response:     
                if response.status == 200:
                    try:
                        text = await response.text()
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
                    logger.error(f"Request error, status code is {response.status}")

async def process_requests(search_queries):
    tasks = []
    
    for query in search_queries:
        task = asyncio.create_task(get_data(query))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    processed_results = []
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({"query": search_queries[idx], "error": str(result)})
        else:
            processed_results.append({"query": search_queries[idx], "data": result})
    
    return processed_results

async def data_validation(response):
    try:
        logger.info("Validating extracted data.")
        products = response['data']['products']
        for product in products:
            price_details = product.get('sizes', [{}])[0].get('price', {})
            basic_price = price_details.get('basic')
            product_price = price_details.get('product')
            total_price = price_details.get('total')

            if all([basic_price, product_price, total_price]):
                return response
                
        raise InvalidContentJSON()
    
    except InvalidContentJSON:
        logger.error("Invalid JSON content.")
        return None

def get_basket_number(id):
    vol = id // 100000
    if 0 <= vol <= 143:
        return "01"
    elif 144 <= vol <= 287:
        return "02"
    elif 288 <= vol <= 431:
        return "03"
    elif 432 <= vol <= 719:
        return "04"
    elif 720 <= vol <= 1007:
        return "05"
    elif 1008 <= vol <= 1061:
        return "06"
    elif 1062 <= vol <= 1115:
        return "07"
    elif 1116 <= vol <= 1169:
        return "08"
    elif 1170 <= vol <= 1313:
        return "09"
    elif 1314 <= vol <= 1601:
        return "10"
    elif 1602 <= vol <= 1655:
        return "11"
    elif 1656 <= vol <= 1919:
        return "12"
    elif 1920 <= vol <= 2045:
        return "13"
    elif 2046 <= vol <= 2189:
        return "14"
    elif 2190 <= vol <= 2405:
        return "15"         
    else:
        return "16"

async def get_details_from_json(session, response):
    logger.info("Formatting data.")
    data_list = []
    for data in response['data']['products']:
        id = data.get('id')
        name = data.get('name')
        cashback = data.get('feedbackPoints')
        sale = data.get('sale')
        brand = data.get('brand')
        rating = data.get('rating')
        supplier = data.get('supplier')
        supplierRating = data.get('supplierRating')
        feedbacks = data.get('feedbacks')
        reviewRating = data.get('reviewRating')
        promoTextCard = data.get('promoTextCard')
        promoTextCat = data.get('promoTextCat')
        price_details = data.get('sizes', [{}])[0].get('price', {})
        basic_price = (price_details.get('basic') / 100)
        product_price = (price_details.get('product') / 100)
        total_price = (price_details.get('total') / 100)
        logistics_price = price_details.get('logistics')
        return_price = price_details.get('return')
        basket_number = get_basket_number(id)
        description = await get_description(session, id, basket_number)

        if basket_number in ["01"]:
            img_url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:2]}/part{str(id)[:4]}/{str(id)}/images/big/1.webp"
        elif basket_number in ["02", "03", "04", "05"]:
            img_url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:3]}/part{str(id)[:5]}/{str(id)}/images/big/1.webp"
        else:
            img_url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:4]}/part{str(id)[:6]}/{str(id)}/images/big/1.webp"

        data_list.append({
            'id_src': id,
            'name': name,
            'cashback': cashback,
            'sale': sale,
            'brand': brand,
            'rating': rating,
            'supplier': supplier,
            'supplierRating': supplierRating,
            'feedbacks': feedbacks,
            'reviewRating': reviewRating,
            'promoTextCard': promoTextCard,
            'promoTextCat': promoTextCat,
            'basic_price': basic_price,
            'product_price': product_price,
            'total_price': total_price,
            'logistics_price': logistics_price,
            'return_price': return_price,
            'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/detail.aspx?targetUrl=BP',
            'img_url': img_url,
            'description': description
        })
    logger.info("Parse Wildberries operation successfull. Sending data.")
    return data_list
