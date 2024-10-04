from fastapi import FastAPI, HTTPException
from sbvirtualdisplay import Display
from contextlib import asynccontextmanager

from app.wildberries.parser import get_data, process_requests
from app.ozon.parser import ozon_parser
from app.yandex.parser import yandex_parser
from app.utils.app_logger import get_logger 

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Launching API and Virtual Display.")
    virtual_display = Display()
    
    try:
        virtual_display.start()
        if virtual_display.is_alive():
            logger.info("Virtual Display started successfully.")
        else:
            logger.warning("Virtual Display may not have started correctly.")
    except OSError as e:
        logger.error(f"OSError while starting Virtual Display: {str(e)}")
    except RuntimeError as e:
        logger.error(f"RuntimeError while starting Virtual Display: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error starting Virtual Display: {str(e)}")
    
    yield
    
    virtual_display.stop()
    logger.info("Stopping API and Virtual Display. Exiting...")


app = FastAPI(lifespan=lifespan)


@app.get("/search/wb")
async def search_single_wb(query: str):
    try:
        logger.info(f"New single request for WB: {query}.")
        data = await get_data(query)
        return {"query": query, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/wb/multiple")
async def search_multiple_wb(queries: list[str]):
    try:
        logger.info("New multiple request for WB.")
        results = await process_requests(queries)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/search/ozon")
def search_single_ozon(query: str, limit: int):
    try:
        logger.info(f"New single request for Ozon: {query}.")
        data = ozon_parser(query, limit)
        return {"query": query, "limit": limit, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/ozon/multiple")
async def search_multiple_ozon(queries: list[str]):
    try:
        pass
    except Exception as e:
        print(e)


@app.get("/search/yandex")
def search_single_yandex(query: str, limit: int):
    try:
        logger.info(f"New single request for Yandex.Market: {query} with limit by {limit}.")
        data = yandex_parser(query, limit)
        return {"query": query, "limit": limit, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/yandex/multiple")
async def search_multiple_yandex(queries: list[str]):
    try:
        pass
    except Exception as e:
        print(e)
