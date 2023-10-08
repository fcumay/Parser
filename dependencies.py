from src.di.app_di import ContainerApp
from src.di.mongo_di import ContainerMongo
from src.di.controller_di import ContainerController
from src.di.kafka_di import ContainerKafka
from src.di.parser_di import ContainerLamodaParser, ContainerTwitchParser


class Dependencies:
    def __init__(self):
        self.container_app = ContainerApp()
        self.container_mongo = ContainerMongo()
        self.container_controller = ContainerController(self.container_mongo.db)
        self.container_lamoda = ContainerLamodaParser(self.container_controller).app
        self.container_twitch = ContainerTwitchParser(self.container_controller).app
        self.container_kafka = ContainerKafka(self.container_lamoda, self.container_twitch)

    def get_kafka(self):
        return self.container_kafka

    def get_controller(self):
        return self.container_controller


dependencies = Dependencies()
