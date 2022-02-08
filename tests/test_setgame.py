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

@pytest.fixture
def cap_set_of_twentyone_cards(deals_extra_cards_after_first_set):
    game = Game(shuffler=lambda x: x)
    game.cards = deals_extra_cards_after_first_set[:]
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

    def test_accept_set_with_valid_set(self, cap_set_of_twelve_or_fewer_cards):
        game = cap_set_of_twelve_or_fewer_cards
        game.start()

        the_set = { 
            Card(Number.THREE, Color.GREEN, Shading.SOLID, Shape.OVAL),
            Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),
            Card(Number.TWO, Color.BLUE, Shading.STRIPED, Shape.DIAMOND)
        }
        result = game.accept_set(the_set)

        assert result
        for card in the_set:
            assert card not in game.board
        assert len(game.board) == 12
        assert len(game.board) + len(game.cards) == 78

    def test_accept_set_with_valid_set_then_greater_than_twelve_cap_set(self, cap_set_of_twentyone_cards):
        game = cap_set_of_twentyone_cards
        game.start()

        the_set = {
            Card(Number.TWO, Color.BLUE, Shading.SOLID, Shape.OVAL),
            Card(Number.TWO, Color.BLUE, Shading.EMPTY, Shape.OVAL),
            Card(Number.TWO, Color.BLUE, Shading.STRIPED, Shape.OVAL),
        }
        result = game.accept_set(the_set)

        assert result
        for card in the_set:
            assert card not in game.board
        assert len(game.board) == 21
        assert len(game.board) + len(game.cards) == 78

    def test_accept_set_with_invalid_set(self, cap_set_of_twelve_or_fewer_cards):
        game = cap_set_of_twelve_or_fewer_cards
        game.start()

        board_copy = game.board[:]
        cards_copy = game.cards.copy()

        the_set = {
            Card(Number.THREE, Color.GREEN, Shading.SOLID, Shape.OVAL),
            Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),
            Card(Number.THREE, Color.RED, Shading.EMPTY, Shape.OVAL)
        }
        result = game.accept_set(the_set)

        assert not result
        assert game.board == board_copy
        assert game.cards == cards_copy

    def test_accept_set_with_invalid_cards(self, cap_set_of_twelve_or_fewer_cards):
        game = cap_set_of_twelve_or_fewer_cards
        game.start()

        board_copy = game.board[:]
        cards_copy = game.cards.copy()

        the_set = {
            Card(Number.ONE, Color.GREEN, Shading.EMPTY, Shape.SQUIGGLE),
            Card(Number.TWO, Color.GREEN, Shading.EMPTY, Shape.OVAL),
            # this card is not on the board
            Card(Number.THREE, Color.GREEN, Shading.EMPTY, Shape.DIAMOND)
        }
        result = game.accept_set(the_set)

        assert not result
        assert game.board == board_copy
        assert game.cards == cards_copy