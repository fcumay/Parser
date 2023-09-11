import asyncio
import uvicorn
from fastapi import APIRouter
from src.models.models_lamoda import Section
from fastapi import Path
from src.di import container_controller
import aioredis
import json
from datetime import datetime
from src.di import container_app
from src.parsers.parser_lamoda import main as lamoda
from src.parsers.parser_twitch import main as twitch

router = APIRouter()


@router.get("/ping")
async def ping() -> dict:
    return {"Success": True}


@router.post("/lamoda/{section}")
async def parse_lamoda(section: Section = Path(...)) -> dict:
    asyncio.create_task(lamoda(section))
    return {"Success": "start_lamoda_parser"}


@router.post("/twitch")
async def parse_twitch() -> dict:
    asyncio.create_task(twitch())
    return {"Success": "start_twitch_parser"}


@router.get("/lamoda")
async def get_lamoda() -> dict:
    global redis_pool
    cached_data = await redis_pool.get("lamoda_data")

    if cached_data:
        return {"data": json.loads(cached_data)}

    data = container_controller.lamoda.get_data_from_mongodb()

    def datetime_handler(x):
        if isinstance(x, datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    json_data = json.dumps([item.dict()
                            for item in data], default=datetime_handler)

    await redis_pool.setex("lamoda_data", 3600, json_data)

    return {"data": data}


@router.get("/twitch/games")
async def get_twitch_games() -> dict:
    global redis_pool

    cached_data = await redis_pool.get("twitch_games_data")

    if cached_data:
        return {"data": json.loads(cached_data)}

    data = container_controller.twitch.get_games_from_mongodb()

    def datetime_handler(x):
        if isinstance(x, datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    json_data = json.dumps([item.dict()
                            for item in data], default=datetime_handler)
    await redis_pool.setex("twitch_games_data", 3600, json_data)

    return {"data": data}


@router.get("/twitch/streams")
async def get_twitch_streams() -> dict:
    global redis_pool
    cached_data = await redis_pool.get("twitch_streams_data")

    if cached_data:
        return {"data": json.loads(cached_data)}

    data = container_controller.twitch.get_streams_from_mongodb()

    def datetime_handler(x):
        if isinstance(x, datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    json_data = json.dumps([item.dict()
                            for item in data], default=datetime_handler)
    await redis_pool.setex("twitch_streams_data", 3600, json_data)

    return {"data": data}


@router.delete("/lamoda/{item_id}")
async def delete_lamoda_by_id(item_id: str) -> dict:
    container_controller.lamoda.delete_data_from_mongodb(item_id)
    return {"Success": f"Deleted item with ID {item_id}"}


@router.delete("/twitch/game/{item_id}")
async def delete_game_by_id(item_id: str) -> dict:
    container_controller.twitch.delete_games_from_mongodb(item_id)
    return {"Success": f"Deleted game with ID {item_id}"}


@router.delete("/twitch/stream/{item_id}")
async def delete_stream_by_id(item_id: str) -> dict:
    container_controller.twitch.delete_streams_from_mongodb(item_id)
    return {"Success": f"Deleted stream with ID {item_id}"}


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
