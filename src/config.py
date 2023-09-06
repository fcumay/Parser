from src.models import Section
from typing import Dict

from pydantic_settings import BaseSettings


class Mongo(BaseSettings):
    mongodb_url: str = "mongodb://mongo_db:27017/new_test_db"


class LamodaUrls(BaseSettings):
    lamoda_urls: Dict[Section, str] = {
        Section.women: "https://www.lamoda.ru/women-home/?sitelink=topmenuW",
        Section.men: "https://www.lamoda.ru/men-home/?sitelink=topmenuM",
        Section.kids: "https://www.lamoda.ru/kids-home/?sitelink=topmenuK"
    }

    lamoda_base: str = "https://www.lamoda.ru"


class Config:
    mongo: Mongo = Mongo()
    lamoda: LamodaUrls = LamodaUrls()
