from confluent_kafka import Producer
from confluent_kafka import Consumer
from src.config import Config


class KafkaDAO:
    def __init__(self):
        self._producer = Producer({'bootstrap.servers': Config.kafka.server})
        self._consumer = Consumer(
            {'bootstrap.servers': Config.kafka.server, 'group.id': 'app_consumer_group', 'auto.offset.reset': 'earliest'})
        self._consumer.subscribe(['parse_task_topic'])

    @property
    def producer(self):
        return self._producer

    @property
    def consumer(self):
        return self._consumer
