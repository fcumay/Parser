from src.di.app_di import ContainerApp
from src.di.mongo_di import ContainerMongo
from src.di.controller_di import ContainerController

container_app = ContainerApp()
container_mongo = ContainerMongo()
container_controller = ContainerController(container_mongo.db)
