from setgame.setgame import Card, Game, Color, Number, Shading, Shape
from web.serialize import BoardSchema

def test_serialize_card():
    game = Game(shuffler=lambda x: x)
    game.start()

    board_schema = BoardSchema()
    cards = board_schema.dump(game)['board']

    assert cards[0] == 'one-red-empty-diamond'