from seleniumwire2 import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException

from curl_cffi import requests
import time
import json
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import pickle
import traceback
from app.utils.app_logger import get_logger

logger = get_logger(__name__)

def firefox_start():
    logger.info("Firefox init.")       
    driver = webdriver.Firefox()
    return driver

def scrolldown(driver, deep):
    for _ in range(deep):
        driver.execute_script('window.scrollBy(0, 500)')
        time.sleep(0.5)

def get_product_info(full_link, sk_value):
    product_id, business_id, sku_id = extract_ids_from_link(full_link)
    if not product_id or not business_id or not sku_id:
        logger.error(f"Error extracting data from link: {full_link}")
        return None

    session = requests.Session()
    url = 'https://market.yandex.ru/api/resolve/?r=src/resolvers/productPage/resolveProductCardRemote:resolveProductCardRemote'

    with open('cookies.pkl', 'rb') as file:
        cookies = pickle.load(file)

    cookie2 = {}
    for cookie in cookies:
        cookie2[cookie['name']] = cookie['value']

    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://market.yandex.ru',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sk': sk_value,
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'x-market-app-version': '2024.09.22.4-desktop.t2585761115',
        'x-market-core-service': '<UNKNOWN>',
        'x-market-front-glue': '1727371608649401',
        'x-market-page-id': 'market:product',
        'x-requested-with': 'XMLHttpRequest',
    }
    
    data = {
        'params': [
            {
                'skuId': sku_id,
                'businessId': business_id,
                'productId': product_id,
            },
        ],
        'path': full_link,
    }
    
    response = session.post(url, impersonate="chrome", cookies=cookie2, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.error("JSON decode error.")
            logger.error(f"Response text: {response.text}")
            return None
    else:
        logger.error(f"Status code error: {response.status_code}")
        logger.error(f"Response text: {response.text}")
        return None

def extract_ids_from_link(link):
    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    product_id = parsed_url.path.split('/')[-1]
    business_id = query_params.get('uniqueId', [None])[0]
    sku_id = query_params.get('sku', [None])[0]
    return product_id, business_id, sku_id

def get_searchpage_cards(driver, url, max_cards):
    driver.get(url)
    driver.save_screenshot('screenshot.png')
    scrolldown(driver, 30)
    time.sleep(1)
    search_page_html = BeautifulSoup(driver.page_source, "html.parser")
    content = search_page_html.find_all(attrs={"data-auto": "snippet-link"})
    logger.info(f"Found {len(content)} product cards on page.")
    with open('search_page_html.html', 'w', encoding='utf-8') as file:
        file.write(str(search_page_html))

    if len(content) >= 3:
        links = set()
        for div in search_page_html.find_all('div'):
                a_tag = div.find('a', href=True)
                if a_tag and 'href' in a_tag.attrs:
                    href = a_tag['href']
                    if href.startswith('/product'):
                        links.add(href)
                        if len(links) >= max_cards:
                            break

        responses = []

        sk_value = get_cookie(driver)
        time.sleep(3)

        for link in list(links):
            try:
                response = get_product_info(link, sk_value)
                if response:
                    responses.append((response, link))
            except Exception as e:
                logger.error(f"Error processing link: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")

        formatted_data_all = []
        for response, link in responses:
            formatted_data = get_details_from_json(response, link)
            formatted_data_all.extend(formatted_data)
        logger.info('Данные отформатированы!')

        return formatted_data_all

def get_cookie(driver):
    wish_list_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button._63Rdu._3PoE9[title="Добавить в избранное"]'))
    )
    wish_list_button.click()
    time.sleep(2)
    cookies = driver.get_cookies()
    with open('cookies.pkl', 'wb') as file:
        pickle.dump(cookies, file)
    sk_value = capture_post_request(driver)
    
    return sk_value

def capture_post_request(driver):
    sk_value = None
    for request in driver.requests:
        if request.method == 'POST' and request.url == 'https://market.yandex.ru/api/resolve/?r=src/resolvers/wishlist/addWishlistItemByReference:addWishlistItemByReference':
            headers = request.headers
            sk_value = headers.get('sk')
            if sk_value:
                logger.info(f"Extracting sk: {sk_value}")
                break
    driver.quit()
    return sk_value

def get_details_from_json(response, full_link):
    data_list = []
    
    for result in response.get('results', []):
        buy_option = result.get('data', {}).get('collections', {}).get('buyOption', {})
        description = result.get('data', {}).get('collections', {}).get('fullDescription', {})
        image = result.get('data', {}).get('collections', {}).get('productCardMeta', {})
        breadcrumbs = result.get('data', {}).get('collections', {}).get('breadcrumbs', {})

        id = None
        name = None
        price = None
        supplier_name = None
        delivery_text = None
        base_price = None
        for key, value in buy_option.items():
            id = value.get('productId')
            name = value.get('title')
            price = value.get('price', {}).get('value')
            supplier_name = value.get('supplierName')
            delivery_text = value.get('deliveryText')
            base_price = value.get('basePrice', {}).get('value')
        
        description_text = None
        for key, value in description.items():
            description_text = value.get('text')

        img_url = None
        feedbacks = None
        reviewRating = None
        brand = None
        for key, value in image.items():
            img_url = value.get('image')
            feedbacks = value.get('ratingCount')
            reviewRating = value.get('rating')
            brand = value.get('vendorName')

        breadcrumb_texts = []
        breadcrumb_params = []
        for key, value in breadcrumbs.items():
            for item in value.get('breadcrumbItems', []):
                breadcrumb_texts.append(item.get('text'))
                breadcrumb_params.append(item.get('transition', {}).get('params', {}))

        breadcrumbs_formatted = {}
        if breadcrumb_texts and breadcrumb_params:
            for i, (text, param) in enumerate(zip(breadcrumb_texts, breadcrumb_params)):
                key = f'name_{i+1}'
                key_eng = f'name_{i+1}_eng'
                breadcrumbs_formatted[key] = text
                breadcrumbs_formatted[key_eng] = param.get('categorySlug')

        data_list.append({
            'id_src': id,
            'name': name,
            'brand': brand,
            'product_price': price,
            'supplier': supplier_name,
            'feedbacks':feedbacks,
            'reviewRating':reviewRating,
            'delivery_text': delivery_text,
            'basic_price': base_price,
            'link': f"https://market.yandex.ru/{full_link}",
            'img_url': img_url,
            'description': description_text,
            'category': breadcrumbs_formatted
        })
    
    return data_list

def yandex_parser(query, limit):
    logger.info("Starting Firefox Session")
    driver = firefox_start()
    logger.info("Starting gathering product information.")
    while True:
        count = 0
        url_search = f"https://market.yandex.ru/search?text={query}"
        try:
            data = get_searchpage_cards(driver, url_search, limit)
            break
        except Exception as e:
            if count != 10:
                logger.error(f"Processing request error for {query}.")
                logger.error(f"Exception details: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.info("Closing Firefox session.")
                driver.quit()
                count = count + 1
                return None
            else:
                data = False
                logger.error("Couldn't catch data from Ya.Market after 10 tries.")
                break
    logger.info("Parse Ya.Market operation successfull. Sending data.")
    return data