from enum import Enum
from pydantic import BaseModel
from datetime import datetime


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
