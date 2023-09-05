import asyncio

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from src.controller import ExceptionMiddleware
from src.parser import main

from fastapi import Path
from src.db import Section, get_data_from_mongodb
import aioredis
import json
from datetime import datetime


async def ping() -> dict:
    return {"Success": True}


async def parse_lamoda(section: Section = Path(...)) -> dict:
    asyncio.create_task(main(section))
    return {"Success": "start_parser"}


# async def get_lamoda()->dict:
#     data = get_data_from_mongodb()
#     return {"data": data}


async def get_lamoda() -> dict:
    data = get_data_from_mongodb()

    def datetime_handler(x):
        if isinstance(x, datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    json_data = json.dumps([item.dict()
                           for item in data], default=datetime_handler)
    await redis_pool.setex("lamoda_data", 3600, json_data)
    return {"data": data}


redis_pool = None


async def startup():
    global redis_pool
    redis_pool = aioredis.from_url("redis://redis_cache:6379")


async def shutdown():
    global redis_pool
    if redis_pool:
        await redis_pool.close()


routes = [
    APIRoute(path="/ping", endpoint=ping, methods=["GET"]),
    APIRoute(path="/lamoda", endpoint=get_lamoda, methods=["GET"]),
    APIRoute(
        path="/lamoda/{section}",
        endpoint=parse_lamoda,
        methods=["POST"]),
]

app = FastAPI()
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
app.include_router(APIRouter(routes=routes))
app.add_middleware(ExceptionMiddleware)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
