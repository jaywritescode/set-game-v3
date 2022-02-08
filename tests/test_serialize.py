import pytest

from setgame.setgame import Card, Game, Color, Number, Shading, Shape
from web.serialize import BoardSchema

@pytest.fixture
def sample_game(shuffled_deck):
    game = Game(shuffler=lambda x: x)
    game.cards = shuffled_deck[:]
    return game

def test_serialize_card():
    game = Game(shuffler=lambda x: x)
    game.start()

    board_schema = BoardSchema()
    cards = board_schema.dump(game)['board']

    assert cards[0] == 'one-red-empty-diamond'

def test_serialize_game(sample_game):
    sample_game.start()

    board_schema = BoardSchema()
    
    assert board_schema.dump(sample_game) == {
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


