from pydantic import BaseModel, Field
from datetime import datetime


class GameModel(BaseModel):
    id: str
    name: str
    creation_time: datetime = Field(default_factory=datetime.now)


class StreamModel(BaseModel):
    id: str
    user_id: str
    user_login: str
    user_name: str
    game_id: str
    game_name: str
    type: str
    title: str
    viewer_count: int
    started_at: str
    language: str
    thumbnail_url: str
    creation_time: datetime = Field(default_factory=datetime.now)
