import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from sbvirtualdisplay import Display
from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.wildberries.parser import get_data
from app.wildberries.database import init_db
from app.wildberries.category_processor import process_and_save
from app.ozon.parser import ozon_parser
from app.yandex.parser import yandex_parser
from app.utils.app_logger import get_logger
from app.middleware import TimingMiddleware
from app.wildberries.shard_parse import parse_dump_shard
from app.config import DATABASE_URL

from app.dev.task_test import long_running_task

logger = get_logger(__name__)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Алгоритм, который выполняется при запуске веб-сервера
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
    
    await init_db(engine)
    logger.info("Database initialized successfully.")

    yield
    
    virtual_display.stop()
    logger.info("Stopping API and Virtual Display. Exiting...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(TimingMiddleware)
task_storage = []

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
    
@app.get("/search/wb/category")
async def search_category():
    try:
        logger.info("Category parse request start")
        await process_and_save(SessionLocal)
        return {"parse_cycle_complete": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/search/wb/category/token-add")
async def token_add():
    return {"add_token": True}

@app.get("/search/wb/category/shard-query")
async def parse_shard_and_dump():
    await parse_dump_shard(SessionLocal)
    return {"parsed-shard-and-query": True}

@app.get("/search/wb/category/full-cycle-parse")
async def full_cycle_parse():
    return {"parse-task-created": True}

@app.get("/search/wb/category/task-list")
async def task_list():
    return {"task-list": list(task_storage.keys())}

@app.post("/start-task")
async def start_task(task_id: str):
    task = asyncio.create_task(get_data(task_id))
    task_storage[task_id] = task
    logger.info(f"Задача по парсингу запущена, запрос: {task_id}")
    return {"status": f"Задача по парсингу запущена, запрос: {task_id}"}

@app.post("/stop-task/{task_id}")
async def stop_task(task_id: str):
    task = task_storage.get(task_id)
    if task and not task.done():
        task.cancel(task_id)
        task.pop(task_id, None)
        logger.info(f"Задача остановлена: {task_id}")
        return {"status": "Задача остановлена"}
    logger.info("Задача не запущена")
    return {"status": "Задача не запущена"}

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
