from bson.objectid import ObjectId
from src.models.models_lamoda import ProductModel


class LamodaController:
    def __init__(self, db):
        self._db = db
        self._collection = db.products

    @property
    def collection(self):
        return self._collection

    def insert_data_into_mongodb(self, section, data):
        for category_name, products in data.items():
            for product in products:
                product_model = ProductModel(
                    section=section,
                    category=category_name,
                    name=product['Name'],
                    price=product['Price'],
                    shop=product['Shop'],
                )
                self._collection.insert_one(product_model.dict())

    def get_data_from_mongodb(self):
        data = []
        for product in self._collection.find():
            product_model = ProductModel(**product)
            data.append(product_model)
        return data[::-1]

    def delete_data_from_mongodb(self, item_id):
        self._collection.delete_one({"_id": ObjectId(item_id)})
