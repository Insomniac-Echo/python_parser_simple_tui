import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from sbvirtualdisplay import Display
from contextlib import asynccontextmanager

from app.wildberries.parser import get_data
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

async def background_task(task):
    try:
        await task
    except Exception as e:
        logger.error(f"Error processing background task: {e}")

@app.get("/search/wb")
async def search_single_wb(query: str):
    try:
        logger.info(f"New single request for WB: {query}.")
        data = await get_data(query)
        return {"query": query, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/ozon")
async def search_single_ozon(query: str, limit: int, background_tasks: BackgroundTasks):
    try:
        logger.info(f"New request for Ozon: {query} with limit by {limit} pieces.")
        task = asyncio.create_task(asyncio.to_thread(ozon_parser, query, limit))
        background_tasks.add_task(background_task, task)
        data = await task
        return {"query": query, "limit": limit, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/yandex")
async def search_single_yandex(query: str, limit: int, background_tasks: BackgroundTasks):
    try:
        logger.info(f"New request for Yandex.Market: {query} with limit by {limit} pieces.")
        task = asyncio.create_task(asyncio.to_thread(yandex_parser, query, limit))
        background_tasks.add_task(background_task, task)
        data = await task
        return {"query": query, "limit": limit, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4)
