from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class Section(str, Enum):
    men = "men"
    women = "women"
    kids = "kids"


class ProductModel(BaseModel):
    section: Section
    category: str
    name: str
    price: int
    shop: str
    creation_time: datetime = Field(default_factory=datetime.now)
