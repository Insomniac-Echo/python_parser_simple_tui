from fastapi import FastAPI
from sbvirtualdisplay import Display
from contextlib import asynccontextmanager

from app.core.database import init_db, engine
from app.core.app_logger import get_logger
from app.core.middleware import TimingMiddleware
from app.api.routes import wb, ozon, yandex

#from app.dev.task_test import long_running_task

logger = get_logger(__name__)

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

app.include_router(wb.router, prefix="/wb", tags=["Wildberries"])
app.include_router(ozon.router, prefix="/ozon", tags=["Ozon"])
app.include_router(yandex.router, prefix="/yandex", tags=["Yandex"])

