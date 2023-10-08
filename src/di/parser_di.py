from src.parsers.parser_lamoda import LamodaParser
from src.parsers.parser_twitch import TwitchParser


class ContainerLamodaParser:
    def __init__(self, container_controller):
        self._container_controller = container_controller
        self._app = LamodaParser(self._container_controller)

    @property
    def app(self) -> LamodaParser:
        return self._app


class ContainerTwitchParser:
    def __init__(self, container_controller):
        self._container_controller = container_controller
        self._app = TwitchParser(self._container_controller)

    @property
    def app(self) -> TwitchParser:
        return self._app
