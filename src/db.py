from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from pydantic_settings import BaseSettings


class Section(str, Enum):
    men = "men"
    women = "women"
    kids = "kids"


class ProductModel(BaseModel):
    section: Section
    category: str
    name: str
    price: str
    shop: str
    creation_time: datetime = None


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://mongo_db:27017/new_men_db"


settings = Settings()


class MongoDBConnection(object):
    def __init__(self, url=settings.MONGODB_URL):
        self.url = url
        self.client = None

    def __enter__(self):
        self.client = MongoClient(self.url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()


mongo = MongoDBConnection()


def insert_data_into_mongodb(section, data):
    with mongo:
        db = mongo.client.new_men_db
        products_collection = db.products
        for category_name, products in data.items():
            for product in products:
                product_model = ProductModel(
                    section=section,
                    category=category_name,
                    name=product['Name'],
                    price=product['Price'],
                    shop=product['Shop'],
                    creation_time=datetime.now()
                )
                products_collection.insert_one(product_model.dict())


def get_data_from_mongodb():
    with mongo:
        db = mongo.client.new_men_db
        products_collection = db.products
        data = []
        for product in products_collection.find():
            product_model = ProductModel(**product)
            data.append(product_model)
        return data
