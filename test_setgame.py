from itertools import product
from setgame import Card, Game, Number, Color, Shading, Shape
import pytest

@pytest.fixture
def at_least_one_set_in_first_twelve_cards():
    game = Game(shuffler=lambda x: x)
    
    # the three highlighted cards make a set
    initial_cards = [
        Card(Number.ONE, Color.BLUE, Shading.SOLID, Shape.SQUIGGLE),    # this one
        Card(Number.TWO, Color.BLUE, Shading.EMPTY, Shape.DIAMOND), 
        Card(Number.ONE, Color.GREEN, Shading.STRIPED, Shape.SQUIGGLE), # this one
        Card(Number.TWO, Color.RED, Shading.EMPTY, Shape.SQUIGGLE), 
        Card(Number.TWO, Color.GREEN, Shading.SOLID, Shape.SQUIGGLE), 
        Card(Number.THREE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE), 
        Card(Number.ONE, Color.GREEN, Shading.SOLID, Shape.SQUIGGLE), 
        Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),     # and this one
        Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.OVAL), 
        Card(Number.THREE, Color.BLUE, Shading.EMPTY, Shape.OVAL), 
        Card(Number.TWO, Color.BLUE, Shading.SOLID, Shape.OVAL), 
        Card(Number.ONE, Color.BLUE, Shading.STRIPED, Shape.OVAL)
    ]
    for i in initial_cards:
        game.cards.remove(i)
    game.cards = initial_cards + game.cards
    return game

@pytest.fixture
def cap_set_of_sixteen_cards():
    game = Game(shuffler=lambda x: x)

    numbers = [Number.ONE, Number.TWO]
    colors = [Color.RED, Color.BLUE]
    shadings = [Shading.EMPTY, Shading.SOLID]
    shapes = [Shape.DIAMOND, Shape.OVAL]

    initial_cards = [Card(*attrs) for attrs in product(numbers, colors, shadings, shapes)]
    for i in initial_cards:
        game.cards.remove(i)
    game.cards = initial_cards + game.cards
    return game


class TestGame:
    def test_start_with_at_least_one_set_in_first_twelve_cards(self, at_least_one_set_in_first_twelve_cards):
        at_least_one_set_in_first_twelve_cards.start()

        assert len(at_least_one_set_in_first_twelve_cards.board) == 12
        assert len(at_least_one_set_in_first_twelve_cards.board) + len(at_least_one_set_in_first_twelve_cards.cards) == 81

    def test_start_with_no_sets_in_the_first_twelve_cards(self, cap_set_of_sixteen_cards):
        cap_set_of_sixteen_cards.start()

        assert len(cap_set_of_sixteen_cards.board) == 18
        assert len(cap_set_of_sixteen_cards.board) + len(cap_set_of_sixteen_cards.cards) == 81