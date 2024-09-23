from fastapi import FastAPI, HTTPException
from app.wildberries.parser import get_data, process_requests

app = FastAPI()


@app.get("/search/wb/{query}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)