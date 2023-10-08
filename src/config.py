from src.models.models_lamoda import Section
from typing import Dict

from pydantic_settings import BaseSettings


class Mongo(BaseSettings):
    mongodb_url: str = "mongodb://mongo_db:27017/test2"


class LamodaUrls(BaseSettings):
    lamoda_urls: Dict[Section, str] = {
        Section.women: "https://www.lamoda.ru/women-home/?sitelink=topmenuW",
        Section.men: "https://www.lamoda.ru/men-home/?sitelink=topmenuM",
        Section.kids: "https://www.lamoda.ru/kids-home/?sitelink=topmenuK"
    }

    lamoda_base: str = "https://www.lamoda.ru"


class Twitch(BaseSettings):
    client_id: str = "7farkw03xdeuwbwduvvy8ee3wpcsar"
    client_secret: str = "8k2r1a8zq3dkkt9gychm12vt2mqyna"
    url: str = "https://id.twitch.tv/oauth2/token"
    url_games: str = "https://api.twitch.tv/helix/games/top"
    url_streams: str = "https://api.twitch.tv/helix/streams"

class Kafka(BaseSettings):
    server: str = "kafka:9092"

class Config:
    mongo: Mongo = Mongo()
    lamoda: LamodaUrls = LamodaUrls()
    twitch: Twitch = Twitch()
    kafka: Kafka = Kafka()