from pathlib import Path

from fastapi import FastAPI

try:
    from utils.decorators import utils
    from app.controller import controller, manager, ws_router
except ImportError as ie:
    exit(f"{ie} :: {Path(__file__).resolve()}")


@utils.exception
def init_app() -> FastAPI:
    app: FastAPI = FastAPI(lifespan=controller.lifespan, openapi_url=None)
    app.include_router(ws_router)
    return app

app: FastAPI = init_app()

