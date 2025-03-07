import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.core.app_logger import get_logger

from app.parsers.ozon.parser import ozon_parser
from app.api.back_tasks import background_task

logger = get_logger(__name__)
router = APIRouter()

@router.post("/search")
async def search_single_ozon(query: str, limit: int, background_tasks: BackgroundTasks):
    try:
        logger.info(f"New request for Ozon: {query} with limit by {limit} pieces.")
        task = asyncio.create_task(asyncio.to_thread(ozon_parser, query, limit))
        background_tasks.add_task(background_task, task)
        data = await task
        return {"query": query, "limit": limit, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))