import requests
import json
import time

def get_data():
    urlencode = input('Введите запрос поиска (например, "Телефон"): ')
    url = fr'https://search.wb.ru/exactmatch/ru/common/v7/search?ab_testid=rerank_ksort_promo&appType=1&curr=rub&dest=-284542&query={urlencode}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'

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
    
    while True:  # Делаем запросы, пока не выйдем из букса
        try:
            response = requests.get(url, headers=headers).json()

            # проверяем верность запроса по наличию basic_price product_price total_price
            if 'data' in response and 'products' in response['data']:
                products = response['data']['products']
                for product in products:
                    price_details = product.get('sizes', [{}])[0].get('price', {})
                    basic_price = price_details.get('basic')
                    product_price = price_details.get('product')
                    total_price = price_details.get('total')

                    # если какой-то из этих параметров None делаем снова
                    if basic_price is not None and product_price is not None and total_price is not None:
                        with open('wb_poisk_data.json', 'w', encoding='UTF-8') as file:
                            json.dump(response, file, indent=2, ensure_ascii=False)
                            print(f'Данные сохранены в wb_poisk_data.json')
                        return response
                    else:
                        print("Ожидаем валидные данные о ценах. Повтор запроса")
                        time.sleep(2)
            else:
                raise ValueError("Неправильный формат ответа JSON")

        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Ошибка: {e}. Повтор запроса через 2 секунды")
            time.sleep(2)

def get_data_from_json(json_file):
    """Извлекаем из json данные"""
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
        basic_price = price_details.get('basic')
        product_price = price_details.get('product')
        total_price = price_details.get('total')
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
    export = get_data_from_json(get_data())
    save_data_to_json(export, 'extracted_data.json')
