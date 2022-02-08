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
                'three-green-solid-oval',
                'one-red-empty-squiggle',
                'three-red-empty-oval',
                'two-blue-striped-diamond',
                'two-green-solid-diamond',
                'two-green-solid-squiggle',
                'one-red-solid-squiggle',
                'one-green-empty-squiggle',
                'two-green-empty-oval',
                'one-blue-solid-diamond',
                'three-red-solid-oval',
                'one-red-solid-diamond',
            ]
        }