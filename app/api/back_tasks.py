from app.core.app_logger import get_logger

logger = get_logger(__name__)

async def background_task(task):
    try:
        await task
    except Exception as e:
        logger.error(f"Error processing background task: {e}")