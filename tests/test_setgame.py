from itertools import product
import marshmallow_dataclass
import pytest

from setgame.setgame import Card, Game, Number, Color, Shading, Shape

CardSchema = marshmallow_dataclass.class_schema(Card)()

@pytest.fixture
def cap_set_of_twelve_or_fewer_cards(shuffled_deck):
    game = Game(shuffler=lambda x: x)
    game.cards = shuffled_deck[:]
    return game

@pytest.fixture
def cap_set_of_sixteen_cards(needs_extra_cards):
    game = Game(shuffler=lambda x: x)
    game.cards = needs_extra_cards[:]
    return game

class TestGame:
    def test_start_with_at_least_one_set_in_first_twelve_cards(self, cap_set_of_twelve_or_fewer_cards):
        cap_set_of_twelve_or_fewer_cards.start()

        assert len(cap_set_of_twelve_or_fewer_cards.board) == 12
        assert len(cap_set_of_twelve_or_fewer_cards.board) + len(cap_set_of_twelve_or_fewer_cards.cards) == 81

    def test_start_with_no_sets_in_the_first_twelve_cards(self, cap_set_of_sixteen_cards):
        cap_set_of_sixteen_cards.start()

        assert len(cap_set_of_sixteen_cards.board) == 18
        assert len(cap_set_of_sixteen_cards.board) + len(cap_set_of_sixteen_cards.cards) == 81