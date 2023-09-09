from src.controllers.controller_lamoda import LamodaController
from src.controllers.controller_twitch import TwitchController


class ContainerController:
    def __init__(self, db):
        self._lamoda = LamodaController(db)
        self._twitch = TwitchController(db)

    @property
    def lamoda(self):
        return self._lamoda

    @property
    def twitch(self):
        return self._twitch
