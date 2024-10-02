from fastapi import FastAPI, HTTPException, Query
from sbvirtualdisplay import Display
from contextlib import asynccontextmanager

from app.wildberries.parser import get_data, process_requests
from app.ozon.parser import chrome_start, get_searchpage_cards, ozon_parser
from app.yandex.parser import yandex_parser


virtual_display = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global virtual_display
    virtual_display = Display()
    virtual_display.start()
    yield
    virtual_display.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/search/wb")
async def search(query: str):
    try:
        print(query)
        data = await get_data(query)
        return {"query": query, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/wb/multiple")
async def search_multiple(queries: list[str]):
    try:
        results = await process_requests(queries)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/search/ozon/{query}")
async def search(query: str):
    try:
        print(query)
        data = ozon_parser(query)
        return {"query": query, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/ozon/multiple")
async def search_multiple(queries: list[str]):
    try:
        pass
    except:
        pass


@app.get("/search/yandex/{query}")
def search(query: str):
    try:
        print(query)
        data = yandex_parser(query)
        return {"query": query, "data": data}
    except:
        raise HTTPException(status_code=500, detail="Произошла ошибка при парсинге")