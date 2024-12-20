import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.app_logger import get_logger

logger = get_logger(__name__)
# По сути эта штука просто ловить запрос и замеряет время, импортируется прямиком основной код сервера
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Проверяем, относится ли запрос к Wildberries (чтобы кетчить для замера времени ответа)
        if request.url.path.startswith("/search/wb"):
            start_time = time.perf_counter()
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            logger.info(f"Request to {request.url.path} processed in {process_time:.4f} seconds")
            response.headers["X-Process-Time"] = str(process_time)  # Опциональная строка, позволяет закинуть время ответа в хидеры
            return response
        return await call_next(request)
