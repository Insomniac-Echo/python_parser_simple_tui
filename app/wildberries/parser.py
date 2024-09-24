import json
import asyncio
import aiohttp
from app.wildberries.entities import InvalidStatusCodeError, DecodeJSONError, DataValidationError, InvalidContentJSON
       
       
async def get_data(query):
    
    url = fr'https://search.wb.ru/exactmatch/ru/common/v7/search?ab_testid=rerank_ksort_promo&appType=1&curr=rub&dest=-284542&query={query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
    print(url)
    
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
                            print('Вытащили данные!')
                            return get_details_from_json(data)  
                        else:
                            raise DataValidationError("Неверная выдача запроса. Поторная попытка через 3 секунды.")  
                    except json.JSONDecodeError:
                        raise DecodeJSONError("Не удалось декодировать JSON.")
                    except DataValidationError:
                        await asyncio.sleep(3)
                else:
                    raise InvalidStatusCodeError(f"Ошибка запроса, статус-код: {response.status}")

        
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
        print('Проверяем данные!')
        products = response['data']['products']
        for product in products:
            price_details = product.get('sizes', [{}])[0].get('price', {})
            basic_price = price_details.get('basic')
            product_price = price_details.get('product')
            total_price = price_details.get('total')

            if all([basic_price, product_price, total_price]):
                return response
                
        raise InvalidContentJSON("Ожидаем валидные данные о ценах. Повтор запроса")
    
    except InvalidContentJSON as e:
        print(f"Исключение: {e}")
        return None

def get_details_from_json(response):
    print('Форматируем данные!')
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

        data_list.append({
            'id': id,
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
            'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/detail.aspx?targetUrl=BP'
        })
    return data_list
