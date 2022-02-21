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

def test_page_loads(server, page):
    page.goto("http://localhost:3001")
    assert page.title() == "set game"

def test_first_player(server, page):
    page.goto("http://localhost:3001")
    players_el = page.locator('.players .player')
    assert players_el.count() == 1

def test_multiple_players(server, browser):
    pages = [browser.new_context().new_page() for _ in range(4)]
    
    for page in pages:
        page.goto("http://localhost:3001")

    def make_players_locator(page):
        return page.locator('.players .player')

    for page in pages:
        assert make_players_locator(page).count() == 4