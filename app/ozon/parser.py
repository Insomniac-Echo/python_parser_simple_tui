import undetected_chromedriver as uc
from curl_cffi import requests
import time
import json
import re
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from app.ozon.entities import InvalidCardProccesing
from app.utils.app_logger import get_logger

logger = get_logger(__name__)

def chrome_start(url):
    logger.info("Chrome init.")
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-blink-features")
    options.add_argument('--disable-dev-shm-usage')        
    driver = uc.Chrome(options = options, version_main=129)
    return driver

def scrolldown(driver, num_scrolls):
    for _ in range(num_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)

def get_product_info(product_url):
    session = requests.Session()
    raw_data = session.get("https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=" + product_url)
    json_data = json.loads(raw_data.content.decode())
    full_name = json_data["seo"]["title"]
    
    if json_data["layout"][0]["component"] == "userAdultModal":
        product_id = str(full_name.split()[-1])[1:-1]
        return (product_id, full_name, "Товар для лиц старше 18 лет", None, None, None, None)
    else:
        script_data = json.loads(json_data["seo"]["script"][0]["innerHTML"])
        description = script_data.get("description", None)
        image_url = script_data.get("image", None)
        brand = script_data.get("brand", None)
        price = script_data["offers"].get("price", "N/A")
        rating = script_data.get("aggregateRating", {}).get("ratingValue", None)
        rating_counter = script_data.get("aggregateRating", {}).get("reviewCount", None)
        product_id = script_data.get("sku", None)
        layout_tracking_info_str = json_data.get("layoutTrackingInfo", {})
        layout_tracking_info = json.loads(layout_tracking_info_str)
        hierarchy = layout_tracking_info.get("hierarchy", None)
        breadcrumbs_value = json_data["widgetStates"].get("breadCrumbs-3385917-default-1", None)

        breadcrumbs_data = {}
        if breadcrumbs_value:
            breadcrumbs_value = json.loads(breadcrumbs_value)
            breadcrumbs = breadcrumbs_value.get("breadcrumbs", [])
            for i, category in enumerate(breadcrumbs[:-1]):
                breadcrumbs_data[f"name_{i+1}"] = category.get("text")
                breadcrumbs_data[f"name_{i+1}_eng"] = re.sub(r'-\d+/?$', '', category.get("link").replace("/category/", ""))

        if rating is None or rating_counter is None:
            rating = 0.0
            rating_counter = 0

        return (brand, product_id, full_name, description, price, rating, rating_counter, image_url, breadcrumbs_data, hierarchy)

def clean_url(url):#чистим говняные ссылки
    parsed_url = urlparse(url)
    clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return clean_url

def get_searchpage_cards(driver, url, limit, all_cards=None):
    if all_cards is None:
        all_cards = []
    
    logger.info("Gathering product card info.")
    driver.get(url)
    scrolldown(driver, 50)
    search_page_html = BeautifulSoup(driver.page_source, "html.parser")

    content = search_page_html.find("div", {"id": "layoutPage"})
    content = content.find("div")

    content_with_cards = content.find("div", {"class": "widget-search-result-container"})
    content_with_cards = content_with_cards.find("div").findChildren(recursive=False)

    cards_in_page = list()
    logger.info("Starting gathering product information.")
    for card in content_with_cards:
        try:
            card_url = card.find("a", href=True)["href"]
            card_name = card.find("span", {"class": "tsBody500Medium"}).contents[0]

            clean_card_url = clean_url(card_url)
            product_url = "https://ozon.ru" + clean_card_url
            brand, product_id, full_name, description, price, rating, rating_counter, image_url, breadcrumbs_value, hierarchy = get_product_info(clean_card_url)
            card_info = {
                "id_src": int(product_id),
                "short_name": card_name,
                "name": full_name,
                "brand": brand,
                "reviewRating": float(rating),
                "feedbacks": int(rating_counter),
                "product_price": int(price),
                "link": product_url,
                "img_url": image_url,
                "description": description,
                "full_category": hierarchy,
                "category": breadcrumbs_value
            }
            cards_in_page.append(card_info)
        except Exception as e:
            logger.warning(f"Error processing card: {card}")
            logger.error(f"Error message: {e}")

    content_with_next = [div for div in content.find_all("a", href=True) if "Дальше" in str(div)]
    if not content_with_next or (limit is not None and len(all_cards) + len(cards_in_page) >= limit):
        all_cards.extend(cards_in_page)
        return all_cards[:limit]
    else:
        next_page_url = "https://www.ozon.ru" + content_with_next[0]["href"]
        all_cards.extend(cards_in_page)
        return get_searchpage_cards(driver, next_page_url, limit, all_cards)

def ozon_parser(query, limit):
    url = "https://ozon.ru/"
    
    logger.info("Starting Chrome session.")
    driver = chrome_start(url)
    
    while True:
        url_search = f"https://www.ozon.ru/search/?text={query}&from_global=true"
        try:
            search_cards = get_searchpage_cards(driver, url_search, limit)
            cards_quantity = len(search_cards)
            logger.info(f"Successfully found {cards_quantity} by search request {query}")
            break
        except InvalidCardProccesing:
            logger.error("Product card processing error.")
    driver.quit()
    
    logger.info("Parse Ozon operation successfull. Sending data.")
    return search_cards