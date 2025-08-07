from app.parsers.wildberries.entities import InvalidContentJSON
from app.core.app_logger import get_logger

logger = get_logger(__name__)

#Базовая проверка на пригодность JSON для последующей обработки,
#возможно, в будущем будет deprecated из-за внедрения pydantic.
async def data_validation(response):

    try:
        logger.debug("Starting data validation.")

        if not isinstance(response, dict) or 'data' not in response:
            logger.error("Response is missing 'data' field")
            return None

        products = response['data'].get('products')
        if not isinstance(products, list):
            logger.warning("Missing or invalid 'products' field")
            return None

        if not products:
            logger.warning("Products list is empty")
            return None

        sample_product = products[0]
        if not (isinstance(sample_product, dict) and 'id' in sample_product and 'name' in sample_product):
            logger.warning("Product data is incomplete")
            return None

        logger.info(f"Validation passed. Found {len(products)} products.")
        return response

    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        return None
