import sys
import signal
import asyncio
import contextlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

try:
    from main import init_app
except ImportError as ie:
    exit(f"{ie} :: {Path(__file__).resolve()}")


@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_multiple_websocket_connection(client: TestClient):
    num_connections: int = 5
    with contextlib.ExitStack() as stack:
        websockets: list = [
            stack.enter_context(client.websocket_connect("/ws"))
            for _ in range(num_connections)
        ]

        for ws in websockets:
            data = ws.receive_json()
            assert data["type"] == "CONNECT"
            assert "connection was established" in data["message"]

        await asyncio.sleep(10)

        for ws in websockets:
            data: dict = ws.receive_json()
            assert data["type"] == "INFO"
            assert "keep-alive" in data["message"]

        await asyncio.sleep(2)

        for ws in websockets:
            ws.close()
            data: dict = ws.receive_json()
            assert data["type"] == "DISCONNECT"


@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_app_shutdown():
    process: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1", "--port", "8000",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    async def read_output(stream):
        lines = list()
        while True:
            line: bytes = await stream.readline()
            if not line:
                break
            decoded: str = line.decode().strip()
            lines.append(decoded)
        return lines

    read_task: asyncio.Task = asyncio.create_task(read_output(process.stdout))
    await asyncio.sleep(3)
    process.send_signal(signal.SIGTERM)
    await process.wait()
    output_lines = await read_task

    assert process.returncode == -15
    assert any("received signal :: SIGTERM" in line for line in output_lines)
    assert any("no active clients" in line for line in output_lines)
