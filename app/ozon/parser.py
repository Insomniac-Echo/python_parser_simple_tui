import undetected_chromedriver as uc
from curl_cffi import requests
import time
import json
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup

def chrome_start(url):
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-blink-features")
    driver = uc.Chrome(options = options, version_main=128)
    return driver

def scrolldown(driver, deep):
    for _ in range(deep):
        driver.execute_script('window.scrollBy(0, 500)')
        time.sleep(0.17)

def get_product_info(product_url):
    session = requests.Session()
    raw_data = session.get("https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=" + product_url)
    json_data = json.loads(raw_data.content.decode())
    full_name = json_data["seo"]["title"]
    
    if json_data["layout"][0]["component"] == "userAdultModal":
        product_id = str(full_name.split()[-1])[1:-1]
        return (product_id, full_name, "Товар для лиц старше 18 лет", None, None, None, None)
    else:
        script_data = json.loads(json_data["seo"]["script"][0]["innerHTML"])#по ключу seo и script делаем основной поиск, делаем такую же проверку как в скрипте вб через .get, карточки, на которых нет рейтинга или чего-то другого все равно записываем, но на пустых местах ставим non
        description = script_data.get("description", None)
        image_url = script_data.get("image", None)
        price = script_data["offers"].get("price", "N/A") + " " + script_data["offers"].get("priceCurrency", "N/A")
        rating = script_data.get("aggregateRating", {}).get("ratingValue", None)
        rating_counter = script_data.get("aggregateRating", {}).get("reviewCount", None)
        product_id = script_data.get("sku", None)

        return (product_id, full_name, description, price, rating, rating_counter, image_url)

def clean_url(url):#чистим говняные ссылки
    parsed_url = urlparse(url)
    clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return clean_url

def get_searchpage_cards(driver, url, all_cards=[]):
    driver.get(url)
    scrolldown(driver, 50)
    search_page_html = BeautifulSoup(driver.page_source, "html.parser")

    content = search_page_html.find("div", {"id": "layoutPage"})
    content = content.find("div")

    content_with_cards = content.find("div", {"class": "widget-search-result-container"})
    content_with_cards = content_with_cards.find("div").findChildren(recursive=False)

    cards_in_page = list()
    for card in content_with_cards:
        try:
            card_url = card.find("a", href=True)["href"]
            card_name = card.find("span", {"class": "tsBody500Medium"}).contents[0]#этот класс всегда статичный поэтому по нему ищем

            clean_card_url = clean_url(card_url)
            product_url = "https://ozon.ru" + clean_card_url

            product_id, full_name, description, price, rating, rating_counter, image_url = get_product_info(clean_card_url)# прилетает кортеж из 7 элементов и присваивается данным переменным
            card_info = {product_id: {"short_name": card_name,
                                      "full_name": full_name,
                                      "description": description,
                                      "url": product_url,
                                      "rating": rating,
                                      "rating_counter": rating_counter,
                                      "price": price,
                                      "image_url": image_url
                                      }
                         }
            cards_in_page.append(card_info)
            print(product_id, "- DONE")
        except Exception as e:
            print(f"Error processing card: {card}")
            print(f"Error message: {e}")

    content_with_next = [div for div in content.find_all("a", href=True) if "Дальше" in str(div)]
    if not content_with_next:
        return cards_in_page
    else:
        next_page_url = "https://www.ozon.ru" + content_with_next[0]["href"]
        all_cards.extend(get_searchpage_cards(driver, next_page_url, cards_in_page))
        return all_cards


# def get_mainpage_cards(driver, url):
#     driver.get(url)
#     scrolldown(driver, 50)
#     main_page_html = BeautifulSoup(driver.page_source, "html.parser")
#     fresh_island_elements = main_page_html.find_all(attrs={"data-widget": "freshIsland"}) #ищем "data-widget": "freshIsland"
#     last_fresh_island_element = fresh_island_elements[-1] if fresh_island_elements else None #берем последний элемент data-widget="freshIsland"
    
#     if last_fresh_island_element:
#         # ищем третий div с class="t4j_23" и data-widget="skuGridSimple"
#         sku_grid_div = main_page_html.find_all(attrs={"data-widget": "skuGridSimple"})
        
#         if len(sku_grid_div) >= 3:
#             links = set()  # set фильтрует повторяющиеся линки(охуеть!)
#             for div in main_page_html.find_all('div'): #ищем все дивы
#                 if div.find('span', class_='tsBody500Medium'): #в этих дивах ищем спан с классом tsBody500Medium
#                     a_tag = div.find('a', href=True) # ищем а тэг с href
#                     if a_tag and 'href' in a_tag.attrs:
#                         links.add(a_tag['href'])       
#
#             all_cards = list()
#             for link in links:
#                 try:
#                     product_url = "https://ozon.ru" + link
#                     product_id, full_name, description, price, rating, rating_counter, image_url = get_product_info(link)
#                     card_info = {product_id: {
#                         "short_name": full_name,
#                         "full_name": full_name,
#                         "description": description,
#                         "url": product_url,
#                         "rating": rating,
#                         "rating_counter": rating_counter,
#                         "price": price,
#                         "image_url": image_url
#                     }}
#                     all_cards.append(card_info)
#                     print(product_id, "- DONE")
#                 except Exception as e:
#                     print(f"Error processing card: {link}")
#                     print(f"Error message: {e}")
#                 # print(card_info)    
#             return all_cards

def save_to_json(data, filename="parsed_data.json"):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    print(f'Форматированные данные сохранены в {filename}')

def ozon_parser():
    # get_product_info()
    url = "https://ozon.ru/"
    driver = chrome_start(url)
    end_list = list()
    search_tag = input('Введите запрос поиска (например, "Телефон"): ')
    while True:
        url_search = f"https://www.ozon.ru/search/?text={search_tag}&from_global=true"
        try:
            search_cards = get_searchpage_cards(driver, url_search)
            print("Я успешно нашёл", len(search_cards), "по поиску", search_tag)
            end_list.append({search_tag: search_cards})
            break
        except:
            print("Я упал на", search_tag)
    save_to_json(end_list, "ozon_parsed_data.json")
    # get_mainpage_cards(driver, url)