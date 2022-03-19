import pytest

from setgame.setgame import Card, Game, Color, Number, Shading, Shape
from web.serialize import GameSchema, CardSchema


@pytest.fixture
def sample_game(shuffled_deck):
    game = Game(shuffler=lambda x: x)
    game.cards = shuffled_deck[:]
    return game


def test_serialize_card():
    card = Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.DIAMOND)
    assert CardSchema.dump(card) == {
        "number": "ONE",
        "color": "RED",
        "shading": "EMPTY",
        "shape": "DIAMOND",
    }


def test_deserialize_card():
    card = CardSchema.load(
        {"number": "ONE", "color": "RED", "shading": "EMPTY", "shape": "DIAMOND"}
    )
    assert card == Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.DIAMOND)


def test_serialize_game(sample_game):
    sample_game.add_player("ron")
    sample_game.add_player("jeff")

    sample_game.start()

    the_set = {
        Card(Number.THREE, Color.GREEN, Shading.SOLID, Shape.OVAL),
        Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),
        Card(Number.TWO, Color.BLUE, Shading.STRIPED, Shape.DIAMOND),
    }
    sample_game.accept_set(the_set, player="ron")

    dump = GameSchema().dump(sample_game)
    assert dump["board"] == [
        {"number": "THREE", "color": "RED", "shading": "EMPTY", "shape": "OVAL"},
        {"number": "TWO", "color": "GREEN", "shading": "SOLID", "shape": "DIAMOND"},
        {"number": "TWO", "color": "GREEN", "shading": "SOLID", "shape": "SQUIGGLE"},
        {"number": "ONE", "color": "RED", "shading": "SOLID", "shape": "SQUIGGLE"},
        {"number": "ONE", "color": "GREEN", "shading": "EMPTY", "shape": "SQUIGGLE"},
        {"number": "TWO", "color": "GREEN", "shading": "EMPTY", "shape": "OVAL"},
        {"number": "ONE", "color": "BLUE", "shading": "SOLID", "shape": "DIAMOND"},
        {"number": "THREE", "color": "RED", "shading": "SOLID", "shape": "OVAL"},
        {"number": "ONE", "color": "RED", "shading": "SOLID", "shape": "DIAMOND"},
        {"shape": "SQUIGGLE", "shading": "EMPTY", "number": "ONE", "color": "BLUE"},
        {"shape": "SQUIGGLE", "shading": "STRIPED", "number": "TWO", "color": "GREEN"},
        {"shape": "DIAMOND", "shading": "STRIPED", "number": "TWO", "color": "GREEN"},
    ]

    assert dump["players"]["jeff"] == []
    for i, s in enumerate(dump["players"]["ron"]):
        assert is_permutation(
            s,
            [
                [
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
                        "number": "TWO",
                        "color": "BLUE",
                        "shading": "STRIPED",
                        "shape": "DIAMOND",
                    },
                ]
            ][i],
        )


def is_permutation(m, n):
    for val in m:
        assert val in n
    for val in n:
        assert val in m
    return True
