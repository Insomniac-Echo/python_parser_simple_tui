from app.wildberries.entities import InvalidContentJSON
from app.utils.app_logger import get_logger

logger = get_logger(__name__)

#Базовая проверка на пригодность JSON для последующей обработки,
#возможно, в будущем будет deprecated из-за внедрения pydantic.
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
