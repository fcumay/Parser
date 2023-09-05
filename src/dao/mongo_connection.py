# product_dao.py
from datetime import datetime

from src.db import MongoDBConnection
from src.models import ProductModel, Section


class MongoDAO:
    def __init__(self):
        self.mongo = MongoDBConnection()

    def insert_data_into_mongodb(self, section, data):
        with self.mongo:
            db = self.mongo.client.new_men_db
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

    def get_items(self):
        with self.mongo:
            db = self.mongo.client.new_men_db
            products_collection = db.products
            data = []
            for product in products_collection.find():
                product_model = ProductModel(**product)
                data.append(product_model)
            return data
