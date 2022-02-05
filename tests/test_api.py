import json
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from web.api import app


def test_init_no_game():
    client = TestClient(app)
    with client.websocket_connect('/') as websocket:
        websocket.send_json({ 'type': 'init' })
        
        data = websocket.receive_json()
        assert data == { 'type': 'init', 'board': [] }

def test_start_game_not_started():
    client = TestClient(app)
    with client.websocket_connect('/') as websocket:
        websocket.send_json({ 'type': 'init' })
        websocket.receive_json()

        websocket.send_json({ 'type': 'start' })
        data = websocket.receive_json()
        assert data == { 'type': 'start' }