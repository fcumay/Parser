import asyncio
from fastapi import APIRouter
from src.models.models_lamoda import Section, ProductModel
from fastapi import Path, Depends
import aioredis
import json
from datetime import datetime
from dependencies import dependencies
import threading

from src.models.models_twitch import GameModel, StreamModel

router = APIRouter()


async def cache_data(redis_key, data, cache_time=5):
    global redis_pool
    cached_data = await redis_pool.get(redis_key)

    if cached_data:
        return json.loads(cached_data)

    def datetime_handler(x):
        if isinstance(x, datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    json_data = json.dumps([item.dict()
                            for item in data], default=datetime_handler)

    await redis_pool.setex(redis_key, cache_time, json_data)

    return data


@router.post("/lamoda/{section}")
async def parse_lamoda(section: Section = Path(...), container_kafka=Depends(dependencies.get_kafka)) -> dict:
    container_kafka.send_parse_task_to_kafka("parse_lamoda", section)
    return {"Success": "start_lamoda_parser"}


@router.post("/twitch")
async def parse_twitch(container_kafka=Depends(dependencies.get_kafka)) -> dict:
    container_kafka.send_parse_task_to_kafka("parse_twitch")
    return {"Success": "start_twitch_parser"}


@router.get("/lamoda/{limit}")
async def get_lamoda(limit: int, container_controller=Depends(dependencies.get_controller)) -> dict:
    data = container_controller.lamoda.get_data_from_mongodb(limit)
    cached_data = await cache_data("lamoda_data", data)
    return {"data": cached_data}


@router.get("/twitch/games")
async def get_twitch_games(container_controller=Depends(dependencies.get_controller)) -> dict:
    data = container_controller.twitch.get_games_from_mongodb()
    cached_data = await cache_data("twitch_games_data", data)
    return {"data": cached_data}


@router.get("/twitch/streams")
async def get_twitch_streams(container_controller=Depends(dependencies.get_controller)) -> dict:
    data = container_controller.twitch.get_streams_from_mongodb()
    cached_data = await cache_data("twitch_streams_data", data)
    return {"data": cached_data}


@router.put("/lamoda/products/{item_id}")
async def update_data_by_id(item_id: str, update_data: ProductModel,
                            container_controller=Depends(dependencies.get_controller)) -> dict:
    result = container_controller.lamoda.update_data_in_mongodb(
        item_id, update_data.dict())
    if result.modified_count == 0:
        return {"Error": f"No product with ID {item_id} found"}
    return {"Success": f"Updated product with ID {item_id}"}


@router.put("/twitch/games/{item_id}")
async def update_game_by_id(item_id: str, update_data: GameModel,
                            container_controller=Depends(dependencies.get_controller)) -> dict:
    result = container_controller.twitch.update_game_in_mongodb(
        item_id, update_data.dict())
    if result.modified_count == 0:
        return {"Error": f"No game with ID {item_id} found"}
    return {"Success": f"Updated game with ID {item_id}"}


@router.put("/twitch/streams/{item_id}")
async def update_stream_by_id(item_id: str, update_data: StreamModel,
                              container_controller=Depends(dependencies.get_controller)) -> dict:
    result = container_controller.twitch.update_stream_in_mongodb(
        item_id, update_data.dict())
    if result.modified_count == 0:
        return {"Error": f"No stream with ID {item_id} found"}
    return {"Success": f"Updated stream with ID {item_id}"}


@router.delete("/lamoda/{item_id}")
async def delete_lamoda_by_id(item_id: str, container_controller=Depends(dependencies.get_controller)) -> dict:
    container_controller.lamoda.delete_data_from_mongodb(item_id)
    return {"Success": f"Deleted item with ID {item_id}"}


@router.delete("/twitch/game/{item_id}")
async def delete_game_by_id(item_id: str, container_controller=Depends(dependencies.get_controller)) -> dict:
    container_controller.twitch.delete_games_from_mongodb(item_id)
    return {"Success": f"Deleted game with ID {item_id}"}


@router.delete("/twitch/stream/{item_id}")
async def delete_stream_by_id(item_id: str, container_controller=Depends(dependencies.get_controller)) -> dict:
    container_controller.twitch.delete_streams_from_mongodb(item_id)
    return {"Success": f"Deleted stream with ID {item_id}"}


redis_pool = None


async def startup():
    container_kafka = dependencies.get_kafka()
    global redis_pool
    redis_pool = aioredis.from_url("redis://redis_cache:6379")
    consumer_thread = threading.Thread(
        target=lambda: asyncio.run(
            container_kafka.kafka_start()))
    consumer_thread.start()


async def shutdown():
    global redis_pool
    if redis_pool:
        await redis_pool.close()


container_app = dependencies.container_app
container_app.app.add_event_handler("startup", startup)
container_app.app.add_event_handler("shutdown", shutdown)
container_app.app.include_router(router)
