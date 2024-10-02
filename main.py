from fastapi import FastAPI, HTTPException
from sbvirtualdisplay import Display
from contextlib import asynccontextmanager

from app.wildberries.parser import get_data, process_requests
from app.ozon.parser import ozon_parser
from app.yandex.parser import yandex_parser


@asynccontextmanager
async def lifespan(app: FastAPI):
    virtual_display = Display()
    virtual_display.start()
    yield
    virtual_display.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/search/wb")
async def search_single_wb(query: str):
    try:
        print(query)
        data = await get_data(query)
        return {"query": query, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/wb/multiple")
async def search_multiple_wb(queries: list[str]):
    try:
        results = await process_requests(queries)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/search/ozon/{query}")
async def search_single_ozon(query: str):
    try:
        print(query)
        data = ozon_parser(query)
        return {"query": query, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/ozon/multiple")
async def search_multiple_ozon(queries: list[str]):
    try:
        pass
    except Exception as e:
        print(e)


@app.get("/search/yandex/{query}{limit}")
def search_single_yandex(query: str, limit: int):
    try:
        print(query , limit)
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