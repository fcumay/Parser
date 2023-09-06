import asyncio
import uvicorn
from fastapi import APIRouter
from src.models import Section
from src.parser import main
from fastapi import Path
from src.di import container_controller
import aioredis
import json
from datetime import datetime
from src.di import container_app

router = APIRouter()


@router.get("/ping")
async def ping() -> dict:
    return {"Success": True}


@router.post("/lamoda/{section}")
async def parse_lamoda(section: Section = Path(...)) -> dict:
    asyncio.create_task(main(section))
    return {"Success": "start_parser"}


@router.get("/lamoda")
async def get_lamoda() -> dict:
    data = container_controller.lamoda.get_data_from_mongodb()

    def datetime_handler(x):
        if isinstance(x, datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    json_data = json.dumps([item.dict()
                            for item in data], default=datetime_handler)
    await redis_pool.setex("lamoda_data", 3600, json_data)
    return {"data": data}


@router.delete("/lamoda/{item_id}")
async def delete_lamoda_by_id(item_id: str) -> dict:
    container_controller.lamoda.delete_data_from_mongodb(item_id)
    return {"Success": f"Deleted item with ID {item_id}"}


redis_pool = None


async def startup():
    global redis_pool
    redis_pool = aioredis.from_url("redis://redis_cache:6379")


async def shutdown():
    global redis_pool
    if redis_pool:
        await redis_pool.close()


container_app.app.add_event_handler("startup", startup)
container_app.app.add_event_handler("shutdown", shutdown)
container_app.app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(container_app.app, host="0.0.0.0", port=8000)
