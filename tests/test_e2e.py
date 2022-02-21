from multiprocessing import Process
import pytest
from starlette.testclient import TestClient
import uvicorn

from web.api import app


def run_server():
    uvicorn.run(app, host='0.0.0.0', port=3001)

@pytest.fixture
def server():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    yield
    proc.kill()

def test_example_is_working(server, page):
    page.goto("http://localhost:3001")
    assert page.title() == "set game"