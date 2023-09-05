from src.config import MONGODB_URL
from pymongo import MongoClient


class MongoDBConnection(object):
    def __init__(self, url=MONGODB_URL):
        self.url = url
        self.client = None

    def __enter__(self):
        self.client = MongoClient(self.url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()
