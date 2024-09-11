import requests
import json

def get_data():
    url = 'https://catalog.wb.ru/catalog/men_clothes1/v2/catalog?ab_testing=false&appType=1&cat=8144&curr=rub&dest=-1257786&sort=popular&spp=30'
    
    #Для вб эту штуку я бы сделал более гибкой как и юрл обоссаный, это точно нужно доработать, ибо сейчас он по хардкоженой ссылке срёт
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
    if response.status_code == 200:
        print("Запрос успешен, статус-код:", response.status_code)
        print("Время выполнения запроса:", response.elapsed.total_seconds(), "секунд")
        try:
            data = response.json()
            with open('data.json', 'w', encoding='UTF-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
                print(f'Данные сохранены в data.json')
        except ValueError:
            print("Ответ не является JSON")
    else:
        print("Ошибка запроса, статус-код:", response.status_code)
        print("Время выполнения запроса:", response.elapsed.total_seconds(), "секунд")
        pass

def wb_parser():
    #print("wildberries parser placeholder")
    get_data()
