import json
import pytest
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from setgame.setgame import Game
from web.api import app

@pytest.fixture
def sample_game(shuffled_deck):
    game = Game(shuffler=lambda x: x)
    game.cards = shuffled_deck[:]
    return game


def test_init_no_game():
    client = TestClient(app)
    with client.websocket_connect('/') as websocket:
        websocket.send_json({ 'type': 'init' })
        
        data = websocket.receive_json()
        assert data == { 'type': 'init', 'board': [] }

def test_start_game_not_started(sample_game):
    client = TestClient(app)
    with client.websocket_connect('/') as websocket:
        app.state.game = sample_game

        websocket.send_json({ 'type': 'start' })
        data = websocket.receive_json()
        assert data == {
            'type': 'start',
            'board': [
                { 'number': 'THREE', 'color': 'GREEN', 'shading': 'SOLID', 'shape': 'OVAL' },
                { 'number': 'ONE', 'color': 'RED', 'shading': 'EMPTY', 'shape': 'SQUIGGLE' },
                { 'number': 'THREE', 'color': 'RED', 'shading': 'EMPTY', 'shape': 'OVAL' },
                { 'number': 'TWO', 'color': 'BLUE', 'shading': 'STRIPED', 'shape': 'DIAMOND' },
                { 'number': 'TWO', 'color': 'GREEN', 'shading': 'SOLID', 'shape': 'DIAMOND' },
                { 'number': 'TWO', 'color': 'GREEN', 'shading': 'SOLID', 'shape': 'SQUIGGLE' },
                { 'number': 'ONE', 'color': 'RED', 'shading': 'SOLID', 'shape': 'SQUIGGLE' },
                { 'number': 'ONE', 'color': 'GREEN', 'shading': 'EMPTY', 'shape': 'SQUIGGLE' },
                { 'number': 'TWO', 'color': 'GREEN', 'shading': 'EMPTY', 'shape': 'OVAL' },
                { 'number': 'ONE', 'color': 'BLUE', 'shading': 'SOLID', 'shape': 'DIAMOND' },
                { 'number': 'THREE', 'color': 'RED', 'shading': 'SOLID', 'shape': 'OVAL' },
                { 'number': 'ONE', 'color': 'RED', 'shading': 'SOLID', 'shape': 'DIAMOND' },
            ]
        }