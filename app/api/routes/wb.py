import asyncio
from fastapi import APIRouter, HTTPException

from app.parsers.wildberries.category_processor import process_and_save, process_with_workers
from app.parsers.wildberries.parser import get_data
from app.parsers.wildberries.get_shard_query import parse_dump_shard
from app.core.app_logger import get_logger
from app.core.database import SessionLocal
from app.core.task_storage import task_storage

logger = get_logger(__name__)
router = APIRouter()


@router.get("/search")
async def search_single_wb(query: str):
    try:
        logger.info(f"New single request for WB: {query}.")
        data = await get_data(query)
        return {"query": query, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/search/category")
async def search_category():
    try:
        logger.info("Category parse request start")
        await process_and_save(SessionLocal)
        return {"parse_cycle_complete": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/search/category/token-add")
async def token_add():
    return {"add_token": True}

@router.get("/search/category/shard-query")
async def parse_shard_and_dump():
    await parse_dump_shard(SessionLocal)
    return {"parsed-shard-and-query": True}

@router.get("/search/category/full-cycle-parse")
async def full_cycle_parse():
    return {"parse-task-created": True}

@router.get("/search/category/task-list")
async def task_list():
    return {"task-list": list(task_storage.keys())}

@router.post("/start-task")
async def start_task(task_id: str):
    task = asyncio.create_task(get_data(task_id))
    task_storage[task_id] = task
    logger.info(f"Задача по парсингу запущена, запрос: {task_id}")
    return {"status": f"Задача по парсингу запущена, запрос: {task_id}"}

@router.post("/stop-task/{task_id}")
async def stop_task(task_id: str):
    task = task_storage.get(task_id)
    if task and not task.done():
        task.cancel(task_id)
        task.pop(task_id, None)
        logger.info(f"Задача остановлена: {task_id}")
        return {"status": "Задача остановлена"}
    logger.info("Задача не запущена")
    return {"status": "Задача не запущена"}

@router.post("/start-worker-task")
async def start_worker_task(task_id: str):
    if task_id in task_storage:
        raise HTTPException(status_code=400, detail="Task is already running.")

    task = asyncio.create_task(process_with_workers(task_id, SessionLocal))
    task_storage[task_id] = task
    logger.info(f"Task {task_id} started.")
    return {"status": f"Task {task_id} started."}

@router.post("/stop-worker-task/{task_id}")
async def stop_worker_task(task_id: str):
    task = task_storage.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    task.cancel()
    task_storage.pop(task_id, None)
    logger.info(f"Task {task_id} stopped.")
    return {"status": f"Task {task_id} stopped."}

@router.get("/list-tasks")
async def list_task_storage():
    return {"tasks": list(task_storage.keys())}