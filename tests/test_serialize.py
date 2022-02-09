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
        'number': 'ONE',
        'color': 'RED',
        'shading': 'EMPTY',
        'shape': 'DIAMOND'
    }

def test_deserialize_card():
    card = CardSchema.load({ 
        'number': 'ONE',
        'color': 'RED',
        'shading': 'EMPTY',
        'shape': 'DIAMOND'
    })
    assert card == Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.DIAMOND)

def test_serialize_game(sample_game):
    sample_game.start()

    board_schema = GameSchema()
    
    assert board_schema.dump(sample_game) == {
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


