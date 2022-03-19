from assertpy import soft_assertions, assert_that
import pytest
from starlette.testclient import TestClient

from setgame.setgame import Game
from web.api import app

@pytest.fixture
def sample_game(shuffled_deck):
    game = Game(shuffler=lambda x: x)
    game.cards = shuffled_deck[:]
    yield game
    game.reset()


def test_enter_room_empty():
    client = TestClient(app)
    with client.websocket_connect('/') as ws:
        ws.send_json({
            'type': 'enterRoom',
            'payload': {}
        })
        assert_that(app.state.connections.active_connections).is_length(1)

        data = ws.receive_json()
        assert_that(data).is_equal_to({
            'type': 'enterRoom',
            'payload': {
                'board': [],
                'players': {}
            }
        })


def test_enter_room_game_in_progress(sample_game):
    app.state.game = sample_game
    app.state.game.add_player('louis')
    app.state.game.add_player('tom')
    app.state.game.start()

    client = TestClient(app)
    with client.websocket_connect('/') as ws:
        ws.send_json({
            'type': 'enterRoom',
            'payload': {}
        })

        data = ws.receive_json()
        with soft_assertions():
            assert_that(data).has_type('enterRoom')
            assert_that(data['payload']['board']).contains_only(
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
            )
            assert_that(data['payload']['players']).is_equal_to({
                'louis': [],
                'tom': []
            })


def test_join_room_no_players():
    client = TestClient(app)
    with client.websocket_connect('/') as ws:
        ws.send_json({ 'type': 'enterRoom', 'payload': {} })
        ws.receive_json()

        ws.send_json({
            'type': 'joinRoom',
            'payload': { 'playerName': 'todd' }
        })        
        data = ws.receive_json()
        assert_that(app.state.game.players).contains('todd')
        assert_that(data).is_equal_to({
            'type': 'joinRoom',
            'payload': {
                'board': [],
                'players': {
                    'todd': []
                }
            }
        })


def test_join_room_with_multiple_players():
    client = TestClient(app)
    with client.websocket_connect('/') as ws:
        ws.send_json({ 'type': 'enterRoom', 'payload': {} })
        ws.receive_json()
        ws.send_json({
            'type': 'joinRoom',
            'payload': { 'playerName': 'todd' }
        })
        ws.receive_json()

        ws.send_json({ 'type': 'enterRoom', 'payload': {} })
        ws.receive_json()
        ws.send_json({
            'type': 'joinRoom',
            'payload': { 'playerName': 'larry' }
        })
        ws.receive_json()

        ws.send_json({ 'type': 'enterRoom', 'payload': {} })
        ws.receive_json()
        ws.send_json({
            'type': 'joinRoom',
            'payload': { 'playerName': 'frank' }
        })
        data = ws.receive_json()

        assert_that(app.state.game.players).contains('todd', 'larry', 'frank')
        assert_that(data).is_equal_to({
            'type': 'joinRoom',
            'payload': {
                'board': [],
                'players': {
                    'todd': [],
                    'larry': [],
                    'frank': [],
                }
            }
        })


def test_start_game(sample_game):
    app.state.game = sample_game
    app.state.game.add_player('doug')
    app.state.game.add_player('gene')

    client = TestClient(app)
    with client.websocket_connect('/') as ws:
        ws.send_json({ 'type': 'start', 'payload': {} })
        data = ws.receive_json()

        with soft_assertions():
            assert_that(data).has_type('start')
            assert_that(data['payload']['board']).contains_only(
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
            )
            assert_that(data['payload']['players']).is_equal_to({ 'doug': [], 'gene': [] })