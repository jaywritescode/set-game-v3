from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from web.api import app


def test_app():
    client = TestClient(app)
    with client.websocket_connect('/') as websocket:
        websocket.send_text('blah')
        data = websocket.receive_text()
        assert data == 'not json'