import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.core.app_logger import get_logger
from app.api.back_tasks import background_task
from app.parsers.yandex.parser import yandex_parser

logger = get_logger(__name__)
router = APIRouter()

@router.post("/search")
async def search_single_yandex(query: str, limit: int, background_tasks: BackgroundTasks):
    try:
        logger.info(f"New request for Yandex.Market: {query} with limit by {limit} pieces.")
        task = asyncio.create_task(asyncio.to_thread(yandex_parser, query, limit))
        background_tasks.add_task(background_task, task)
        data = await task
        return {"query": query, "limit": limit, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))