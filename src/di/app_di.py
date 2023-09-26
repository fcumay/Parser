from fastapi import FastAPI


class ContainerApp:
    def __init__(self):
        self._app = FastAPI()

    @property
    def app(self) -> FastAPI:
        return self._app
