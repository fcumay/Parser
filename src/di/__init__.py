from src.di.app_di import ContainerApp
from src.di.mongo_di import ContainerMongo
from src.di.controller_di import ContainerController
from src.di.kafka_di import ContainerKafka
from src.di.parser_di import ContainerLamodaParser, ContainerTwitchParser

container_app = ContainerApp()
container_mongo = ContainerMongo()
container_controller = ContainerController(container_mongo.db)
container_lamoda = ContainerLamodaParser(container_controller).app
container_twitch = ContainerTwitchParser(container_controller).app
container_kafka = ContainerKafka(container_lamoda, container_twitch)
