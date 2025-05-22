import sys
import pytest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from main import init_app
except ImportError as ie:
    exit(f"{ie} :: {Path(__file__).resolve()}")


@pytest.fixture(scope="session")
def client():
    app: FastAPI = init_app()
    with TestClient(app) as client:
        yield client
