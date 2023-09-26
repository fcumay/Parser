from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class Section(str, Enum):
    men = "men"
    women = "women"
    kids = "kids"


class ProductModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    section: Section
    category: str
    name: str
    price: int
    shop: str
    creation_time: datetime = Field(default_factory=datetime.now)
