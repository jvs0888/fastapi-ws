from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

try:
    from loggers.logger import logger
    from utils.decorators import utils
    from app.manager import manager
except ImportError as ie:
    exit(f"{ie} :: {Path(__file__).resolve()}")


ws_router: APIRouter = APIRouter(tags=["WebSocket"])


@ws_router.websocket(
    path="/ws",
    name="ws_route"
)
async def ws_route(ws: WebSocket):
    connection_id: str = await manager.connect(ws)

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(connection_id=connection_id)
