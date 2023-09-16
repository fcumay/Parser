from src.di.app_di import ContainerApp
from src.di.mongo_di import ContainerMongo
from src.di.controller_di import ContainerController
from src.di.kafka_di import ContainerKafka

container_app = ContainerApp()
container_mongo = ContainerMongo()
container_controller = ContainerController(container_mongo.db)

from src.parsers.parser_twitch import main as twitch
from src.parsers.parser_lamoda import main as lamoda
container_kafka = ContainerKafka(lamoda, twitch)
