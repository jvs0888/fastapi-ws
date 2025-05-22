import asyncio
from uuid import uuid4
from pathlib import Path

from fastapi import WebSocket

try:
    from loggers.logger import logger
    from utils.decorators import utils
except ImportError as ie:
    exit(f"{ie} :: {Path(__file__).resolve()}")


class ConnectionManager:
    def __init__(self):
        self.active_connections = dict()
        self.shutdown_initiated: bool = False
        self._lock: asyncio.Lock = asyncio.Lock()

    @utils.async_exception
    async def send_message(self, ws: WebSocket, message: str, message_type: str) -> bool:
        try:
            await ws.send_json({"type": message_type, "message": message})
            return True
        except Exception:
            logger.error("message not sent")
            return False

    @utils.async_exception
    async def connect(self, ws: WebSocket) -> str:
        await ws.accept()

        connection_id: str = uuid4().__str__()
        message: str = "connection was established"
        await self.send_message(ws=ws, message=message, message_type="CONNECT")

        async with self._lock:
            self.active_connections[connection_id] = ws
            logger.info(f"new connection :: {connection_id}")

        return connection_id

    @utils.async_exception
    async def disconnect(self, connection_id: str) -> None:
        async with self._lock:
            ws: WebSocket = self.active_connections.pop(connection_id, None)

        if not ws:
            return

        message: str = "connection was disconnected"

        if await self.send_message(ws=ws, message=message, message_type="DISCONNECT"):
            await ws.close(code=1001)

        logger.info(f"client disconnected :: {connection_id}")

    @utils.async_exception
    async def notifications(self, message: str, message_type: str = "INFO") -> None:
        async with self._lock:
            connections = list(self.active_connections.items())

        for connection_id, ws in connections:
            try:
                await self.send_message(ws=ws, message=message, message_type=message_type)
            except Exception:
                await self.disconnect(connection_id=connection_id)

    @utils.async_exception
    async def has_clients(self) -> bool:
        async with self._lock:
            return bool(self.active_connections)

    @utils.async_exception
    async def client_count(self) -> int:
        async with self._lock:
            return len(self.active_connections)

    @utils.async_exception
    async def shutdown_all(self) -> None:
        async with self._lock:
            connections = list(self.active_connections.keys())

        for connection_id in connections:
            await self.disconnect(connection_id=connection_id)


manager: ConnectionManager = ConnectionManager()
