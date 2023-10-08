from src.config import Config
from pymongo import MongoClient


class MongoDAO:
    def __init__(self):
        self.client = MongoClient(Config.mongo.mongodb_url)
        self._db = None

    @property
    def db(self):
        return self.client.db
