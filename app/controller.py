import os
import signal
import asyncio
import threading
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI

try:
    from loggers.logger import logger
    from utils.decorators import utils
    from app.ws_route import manager, ws_router
except ImportError as ie:
    exit(f"{ie} :: {Path(__file__).resolve()}")


class ShutdownController:
    @staticmethod
    @utils.async_exception
    async def shutdown_monitor():
        try:
            shutdown: datetime = datetime.now() + timedelta(minutes=30)

            if await manager.has_clients():
                await manager.notifications(message="connection is closing soon", message_type="WARNING")

                while datetime.now() < shutdown:
                    count: int = await manager.client_count()
                    logger.info(f"waiting for clients to disconnect, connected :: {count}")
                    logger.warning(f"time left :: {(shutdown - datetime.now()).seconds} seconds")

                    if not await manager.has_clients():
                        logger.info("all clients disconnected, proceeding to shutdown")
                        break

                    await asyncio.sleep(5)
            else:
                logger.info("no active clients")

            await manager.shutdown_all()
        finally:
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            os.kill(os.getpid(), signal.SIGTERM)

    @utils.exception
    def handle_signal(self, sig, frame):
        signal_name: str = signal.Signals(sig).name
        logger.info(f"received signal :: {signal_name}")
        manager.shutdown_initiated = True

        loop: asyncio.EventLoop = asyncio.get_event_loop()
        loop.create_task(self.shutdown_monitor())

    @asynccontextmanager
    async def lifespan(self, _: FastAPI):
        if threading.current_thread() == threading.main_thread():
            signal.signal(signal.SIGTERM, self.handle_signal)
            signal.signal(signal.SIGINT, self.handle_signal)

        async def ping():
            while not manager.shutdown_initiated:
                await manager.notifications(message="keep-alive")
                await asyncio.sleep(10)

        asyncio.create_task(ping())

        try:
            yield
        except Exception as e:
            logger.exception(e)


controller: ShutdownController = ShutdownController()
