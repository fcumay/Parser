import asyncio
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
from confluent_kafka import Producer
from confluent_kafka import Consumer, KafkaError
import threading
import logging
from log_config import setup_logging

setup_logging()

producer = Producer({'bootstrap.servers': 'kafka:9092'})
consumer = Consumer(
    {'bootstrap.servers': 'kafka:9092', 'group.id': 'app_consumer_group', 'auto.offset.reset': 'earliest'})
consumer.subscribe(['parse_task_topic'])


async def kafka_start():
    logging.info("Kafka listen")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                logging.error(f"Error:{msg.error()}")
                continue
        logging.info(f"Received message:{msg.error()}")
        parse_task = json.loads(msg.value())
        task_type = parse_task.get("task_type")
        logging.info(f"Task type: {task_type}")
        if task_type == "parse_twitch":
            await twitch()
        elif task_type == "parse_lamoda":
            await lamoda(parse_task.get("other_data"))


async def send_parse_task_to_kafka(key, data=None):
    parse_task = {
        "task_type": key,
        "other_data": data
    }
    logging.info(f"\Send task to kafka")
    producer.produce('parse_task_topic', key=key, value=json.dumps(parse_task))
    producer.flush()


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

    json_data = json.dumps([item.dict() for item in data], default=datetime_handler)

    await redis_pool.setex(redis_key, cache_time, json_data)

    return data


@router.get("/ping")
async def ping() -> dict:
    return {"Success": True}


@router.post("/lamoda/{section}")
async def parse_lamoda(section: Section = Path(...)) -> dict:
    asyncio.create_task(send_parse_task_to_kafka("parse_lamoda", section))
    return {"Success": "start_lamoda_parser"}


@router.post("/twitch")
async def parse_twitch() -> dict:
    asyncio.create_task(send_parse_task_to_kafka("parse_twitch"))
    return {"Success": "start_twitch_parser"}


@router.get("/lamoda")
async def get_lamoda() -> dict:
    data = container_controller.lamoda.get_data_from_mongodb()
    cached_data = await cache_data("lamoda_data", data)
    return {"data": cached_data}


@router.get("/twitch/games")
async def get_twitch_games() -> dict:
    data = container_controller.twitch.get_games_from_mongodb()
    cached_data = await cache_data("twitch_games_data", data)
    return {"data": cached_data}


@router.get("/twitch/streams")
async def get_twitch_streams() -> dict:
    data = container_controller.twitch.get_streams_from_mongodb()
    cached_data = await cache_data("twitch_streams_data", data)
    return {"data": cached_data}


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
    consumer_thread = threading.Thread(target=lambda: asyncio.run(kafka_start()))
    consumer_thread.start()


async def shutdown():
    global redis_pool
    if redis_pool:
        await redis_pool.close()


container_app.app.add_event_handler("startup", startup)
container_app.app.add_event_handler("shutdown", shutdown)
container_app.app.include_router(router)
