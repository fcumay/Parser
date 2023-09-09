from bson.objectid import ObjectId
from src.models.models_twitch import StreamModel, GameModel


class TwitchController:
    def __init__(self, db):
        self._db = db
        self._streams = db.streams
        self._games = db.games

    def insert_streams_into_mongodb(self, streams):
        self._streams.insert_many(streams)

    def insert_games_into_mongodb(self, games):
        self._games.insert_many(games)

    def get_streams_from_mongodb(self):
        data = []
        for stream in self._streams.find():
            stream_model = StreamModel(**stream)
            data.append(stream_model)
        return data

    def get_games_from_mongodb(self):
        data = []
        for game in self._games.find():
            game_model = GameModel(**game)
            data.append(game_model)
        return data

    def delete_streams_from_mongodb(self, item_id):
        self._streams.delete_one({"_id": ObjectId(item_id)})

    def delete_games_from_mongodb(self, item_id):
        self._games.delete_one({"_id": ObjectId(item_id)})
