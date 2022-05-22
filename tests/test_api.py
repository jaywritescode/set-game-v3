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


def test_enter_room_as_first_player():
    client = TestClient(app)
    with client.websocket_connect("/ws") as ws:
        ws.send_json(
            {"type": "enterRoom", "payload": {"playerName": "happy-jackrabbit"}}
        )
        assert_that(app.state.connections.active_connections).is_length(1)

        data = ws.receive_json()
        assert_that(data).is_equal_to(
            {
                "type": "enterRoom",
                "payload": {"board": [], "players": {"happy-jackrabbit": []}},
            }
        )

def test_enter_room_as_second_player():
    client = TestClient(app)
    with client.websocket_connect("/ws") as ws1:
        ws1.send_json(
            {"type": "enterRoom", "payload": {"playerName": "happy-jackrabbit"}}
        )
        ws1.receive_json()  # ignore for test purposes

        with client.websocket_connect("/ws") as ws2:
            ws2.send_json(
                {"type": "enterRoom", "payload": {"playerName": "charming-yeti"}}
            )
            assert_that(app.state.connections.active_connections).is_length(2)

            data1 = ws1.receive_json()
            data2 = ws2.receive_json()
            assert_that(data1['payload']).has_players({"happy-jackrabbit": [], "charming-yeti": []})
            assert_that(data2['payload']).has_players({"happy-jackrabbit": [], "charming-yeti": []})


def test_enter_room_game_in_progress(sample_game):
    app.state.game = sample_game
    app.state.game.add_player("louis")
    app.state.game.add_player("tom")
    app.state.game.start()

    client = TestClient(app)
    with client.websocket_connect("/") as ws:
        ws.send_json({"type": "enterRoom", "payload": {}})

        data = ws.receive_json()
        with soft_assertions():
            assert_that(data).has_type("enterRoom")
            assert_that(data["payload"]["board"]).contains_only(
                {
                    "number": "THREE",
                    "color": "GREEN",
                    "shading": "SOLID",
                    "shape": "OVAL",
                },
                {
                    "number": "ONE",
                    "color": "RED",
                    "shading": "EMPTY",
                    "shape": "SQUIGGLE",
                },
                {
                    "number": "THREE",
                    "color": "RED",
                    "shading": "EMPTY",
                    "shape": "OVAL",
                },
                {
                    "number": "TWO",
                    "color": "BLUE",
                    "shading": "STRIPED",
                    "shape": "DIAMOND",
                },
                {
                    "number": "TWO",
                    "color": "GREEN",
                    "shading": "SOLID",
                    "shape": "DIAMOND",
                },
                {
                    "number": "TWO",
                    "color": "GREEN",
                    "shading": "SOLID",
                    "shape": "SQUIGGLE",
                },
                {
                    "number": "ONE",
                    "color": "RED",
                    "shading": "SOLID",
                    "shape": "SQUIGGLE",
                },
                {
                    "number": "ONE",
                    "color": "GREEN",
                    "shading": "EMPTY",
                    "shape": "SQUIGGLE",
                },
                {
                    "number": "TWO",
                    "color": "GREEN",
                    "shading": "EMPTY",
                    "shape": "OVAL",
                },
                {
                    "number": "ONE",
                    "color": "BLUE",
                    "shading": "SOLID",
                    "shape": "DIAMOND",
                },
                {
                    "number": "THREE",
                    "color": "RED",
                    "shading": "SOLID",
                    "shape": "OVAL",
                },
                {
                    "number": "ONE",
                    "color": "RED",
                    "shading": "SOLID",
                    "shape": "DIAMOND",
                },
            )
            assert_that(data["payload"]["players"]).is_equal_to(
                {"louis": [], "tom": []}
            )


def test_start_game(sample_game):
    app.state.game = sample_game
    app.state.game.add_player("doug")
    app.state.game.add_player("gene")

    client = TestClient(app)
    with client.websocket_connect("/") as ws:
        ws.send_json({"type": "start", "payload": {}})
        data = ws.receive_json()

        with soft_assertions():
            assert_that(data).has_type("start")
            assert_that(data["payload"]["board"]).contains_only(
                {
                    "number": "THREE",
                    "color": "GREEN",
                    "shading": "SOLID",
                    "shape": "OVAL",
                },
                {
                    "number": "ONE",
                    "color": "RED",
                    "shading": "EMPTY",
                    "shape": "SQUIGGLE",
                },
                {
                    "number": "THREE",
                    "color": "RED",
                    "shading": "EMPTY",
                    "shape": "OVAL",
                },
                {
                    "number": "TWO",
                    "color": "BLUE",
                    "shading": "STRIPED",
                    "shape": "DIAMOND",
                },
                {
                    "number": "TWO",
                    "color": "GREEN",
                    "shading": "SOLID",
                    "shape": "DIAMOND",
                },
                {
                    "number": "TWO",
                    "color": "GREEN",
                    "shading": "SOLID",
                    "shape": "SQUIGGLE",
                },
                {
                    "number": "ONE",
                    "color": "RED",
                    "shading": "SOLID",
                    "shape": "SQUIGGLE",
                },
                {
                    "number": "ONE",
                    "color": "GREEN",
                    "shading": "EMPTY",
                    "shape": "SQUIGGLE",
                },
                {
                    "number": "TWO",
                    "color": "GREEN",
                    "shading": "EMPTY",
                    "shape": "OVAL",
                },
                {
                    "number": "ONE",
                    "color": "BLUE",
                    "shading": "SOLID",
                    "shape": "DIAMOND",
                },
                {
                    "number": "THREE",
                    "color": "RED",
                    "shading": "SOLID",
                    "shape": "OVAL",
                },
                {
                    "number": "ONE",
                    "color": "RED",
                    "shading": "SOLID",
                    "shape": "DIAMOND",
                },
            )
            assert_that(data["payload"]["players"]).is_equal_to(
                {"doug": [], "gene": []}
            )
