from src.dao.mongo_connection import MongoDAO


class ContainerMongo:
    def __init__(self):
        self._db = MongoDAO().db

    @property
    def db(self):
        return self._db
