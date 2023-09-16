from src.dao.kafka_connection import KafkaDAO
import json
import logging
from log_config import setup_logging
from confluent_kafka import KafkaError

setup_logging()


class ContainerKafka:
    def __init__(self, lamoda, twitch):
        self._kafka = KafkaDAO()
        self._producer = self._kafka.producer
        self._consumer = self._kafka.consumer
        self._lamoda = lamoda
        self._twitch = twitch

    def send_parse_task_to_kafka(self, key, data=None):
        parse_task = {
            "task_type": key,
            "other_data": data
        }
        logging.info(f"Send task to kafka")
        self._producer.produce(
            'parse_task_topic',
            key=key,
            value=json.dumps(parse_task))
        self._producer.flush()

    async def kafka_start(self):
        logging.info("Kafka listen")
        while True:
            msg = self._consumer.poll(1.0)
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
                await self._twitch()
            elif task_type == "parse_lamoda":
                await self._lamoda(parse_task.get("other_data"))
