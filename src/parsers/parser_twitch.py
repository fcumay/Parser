import asyncio
import httpx
import logging
from log_config import setup_logging
from src.config import Config

setup_logging()


class TwitchParser:
    def __init__(self, controller):
        self.controller = controller

    def _get_access_token(self):
        params = {
            "client_id": Config.twitch.client_id,
            "client_secret": Config.twitch.client_secret,
            "grant_type": "client_credentials"
        }
        with httpx.Client() as client:
            response = client.post(Config.twitch.url, params=params)
            data = response.json()
            if response.status_code == 200:
                access_token = data.get("access_token")
                return access_token
            else:
                logging.error(f"Token error {response.status}")

    async def _get_games(self, headers):
        logging.info(f"Get games")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(Config.twitch.url_games, headers=headers)
                response.raise_for_status()
                games = response.json()
                return games
            except httpx.HTTPError as e:
                logging.exception(f"Get games error: {e}")

    async def _get_streams_streamers(self, headers):
        logging.info(f"Get streams")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(Config.twitch.url_streams, headers=headers)
                response.raise_for_status()
                streams = response.json()
                return streams
            except httpx.HTTPError as e:
                logging.exception(f"Get streams error: {e}")

    async def start_parser(self):
        logging.info(f"Main")
        access_token = self._get_access_token()
        logging.info(f"Access token - {access_token}")
        headers = {
            "Client-ID": Config.twitch.client_id,
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.twitchtv.v5+json"
        }

        try:
            logging.info(f"Start")
            games, streams = await asyncio.gather(self._get_games(headers), self._get_streams_streamers(headers))
            logging.info(f"Continue")
            if games:
                self.controller.twitch.insert_games_into_mongodb(
                    games['data'])
                logging.info("Inserted games data into MongoDB")
            if streams:
                self.controller.twitch.insert_streams_into_mongodb(
                    streams['data'])
                logging.info("Inserted streams data into MongoDB")
            logging.info(f"DONE")
        except Exception as e:
            logging.exception(f"An error occurred: {e}")
