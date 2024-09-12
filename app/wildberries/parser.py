import requests
import json
import time
import sys
from app.wildberries.entities import InvalidStatusCodeError, InvalidContentJSON, DataValidationError
from app.utils.clear import clear_console
       
def get_data(search_input):
    url = fr'https://search.wb.ru/exactmatch/ru/common/v7/search?ab_testid=rerank_ksort_promo&appType=1&curr=rub&dest=-284542&query={search_input}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
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
    
    response = requests.get(url=url, headers=headers)
    
    try:
        if response.status_code == 200:
            print("Запрос успешен, статус-код:", response.status_code)
            print("Время выполнения запроса:", response.elapsed.total_seconds(), "секунд")
            data = response.json()
            with open('data.json', 'w', encoding='UTF-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                    print(f'Данные сохранены в data.json')
                    return data
        else:
            raise InvalidStatusCodeError("Ошибка запроса, статус-код:", response.status_code)
    
    except InvalidStatusCodeError as e:
        print(f"Исключение: {e}")
        print("Время выполнения запроса:", response.elapsed.total_seconds(), "секунд")
        
def data_validation(json_file):
    try:
        products = json_file['data']['products']
        for product in products:
            price_details = product.get('sizes', [{}])[0].get('price', {})
            basic_price = price_details.get('basic')
            product_price = price_details.get('product')
            total_price = price_details.get('total')

            if all([basic_price, product_price, total_price]):
                return json_file
            else:
                raise InvalidContentJSON("Ожидаем валидные данные о ценах. Повтор запроса")
    
    except InvalidContentJSON as e:
        print(f"Исключение: {e}")
        return False

def get_details_from_json(json_file):
    data_list = []
    for data in json_file['data']['products']:
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

def save_data_to_json(data_list: list, filename: str):
    with open(filename, 'w', encoding='UTF-8') as file:
        json.dump(data_list, file, indent=2, ensure_ascii=False)
    print(f'Форматированные данные сохранены в {filename}')

def wb_parser():
    search_request = input('Введите запрос поиска (например, "Телефон"): ')
    while True:
        try:
            export = data_validation(get_data(search_request))
            if export is False:
                raise DataValidationError("Ошибка при получении JSON. Повтор запроса через 3 секунды")
            else:
                save_data_to_json(get_details_from_json(export), 'extracted_data.json')
                sys.exit("Завершение работы.")
            
        except DataValidationError as e:
            print(f"Исключение: {e}")
            time.sleep(3)
            clear_console()
