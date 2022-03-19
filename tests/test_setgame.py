from collections import deque
from unittest.mock import create_autospec
from assertpy import soft_assertions, assert_that
import marshmallow_dataclass
import pytest

from setgame.setgame import Card, Game, Number, Color, Shading, Shape

CardSchema = marshmallow_dataclass.class_schema(Card)()


@pytest.fixture
def test_game():
    return Game(shuffler=lambda x: x)


@pytest.fixture
def standard_game(shuffled_deck, test_game):
    """
    A quote-unquote normal game, where there's always only twelve cards on the board
    and at least one Set on the board.
    """
    test_game.cards = deque(shuffled_deck)
    return test_game


@pytest.fixture
def large_game(needs_extra_cards, test_game):
    """
    No Sets in the first sixteen cards drawn, so we need to draw eighteen to start.
    """
    test_game.cards = deque(needs_extra_cards)
    return test_game


@pytest.fixture
def largest_game(deals_extra_cards_after_first_set, test_game):
    """
    The first three cards drawn form a Set, but then there's no Set in the following
    twenty cards. Any twenty-one cards is guaranteed to have at least one Set.
    """
    test_game.cards = deque(deals_extra_cards_after_first_set)
    return test_game


def test_start():
    def shuffle_fn(game):
        pass

    game = Game(shuffler=create_autospec(shuffle_fn))
    game.start()

    game.shuffler.assert_called()
    assert_that(game.board).is_not_empty()


class TestDeal:
    def test_it_deals_twelve_cards_if_possible(self, standard_game):
        with soft_assertions():
            assert_that(standard_game.deal()).is_true()
            assert_that(standard_game.board).is_length(12)
            assert_that(standard_game.cards).is_length(69)

    def test_it_deals_extra_cards_if_necessary(self, large_game):
        with soft_assertions():
            assert_that(large_game.deal()).is_true()
            assert_that(large_game.board).is_length(18)
            assert_that(large_game.cards).is_length(63)

    def test_it_stops_dealing_at_the_end_of_the_deck(self, large_game):
        with soft_assertions():
            pass


class TestAddPlayer:
    def test_it_adds_a_player(self, standard_game):
        standard_game.add_player("ron")
        standard_game.add_player("jeff")

        assert_that(standard_game.players).is_equal_to({"ron": [], "jeff": []})

    def test_it_can_only_add_a_player_once(self, standard_game):
        standard_game.add_player("ron")
        standard_game.add_player("jeff")

        with pytest.raises(ValueError):
            standard_game.add_player("ron")

        assert_that(standard_game.players).is_equal_to({"ron": [], "jeff": []})


class TestGame:
    def test_accept_set_with_valid_set(self, standard_game):
        standard_game.start()

        standard_game.add_player("ron")
        standard_game.add_player("jeff")

        the_set = {
            Card(Number.THREE, Color.GREEN, Shading.SOLID, Shape.OVAL),
            Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),
            Card(Number.TWO, Color.BLUE, Shading.STRIPED, Shape.DIAMOND),
        }
        result = standard_game.accept_set(the_set, player="ron")

        with soft_assertions():
            assert_that(result).is_true()
            assert_that(standard_game.board).does_not_contain(the_set).is_length(12)
            assert_that(
                list(standard_game.board) + list(standard_game.cards)
            ).is_length(78)
            assert_that(standard_game.players["ron"]).is_equal_to([the_set])
            assert_that(standard_game.players["jeff"]).is_empty()

    def test_accept_set_with_valid_set_then_no_sets_in_next_twenty_cards(
        self, largest_game
    ):
        largest_game.add_player("ron")
        largest_game.add_player("jeff")

        largest_game.start()

        the_set = {
            Card(Number.TWO, Color.BLUE, Shading.SOLID, Shape.OVAL),
            Card(Number.TWO, Color.BLUE, Shading.EMPTY, Shape.OVAL),
            Card(Number.TWO, Color.BLUE, Shading.STRIPED, Shape.OVAL),
        }
        result = largest_game.accept_set(the_set, player="jeff")

        with soft_assertions():
            assert_that(result).is_true()
            assert_that(largest_game.board).does_not_contain(the_set).is_length(21)
            assert_that(list(largest_game.board) + list(largest_game.cards)).is_length(
                78
            )
            assert_that(largest_game.players["jeff"]).is_equal_to([the_set])
            assert_that(largest_game.players["ron"]).is_empty()

    def test_accept_set_fails_with_invalid_set(self, standard_game):
        standard_game.add_player("ron")
        standard_game.add_player("jeff")

        standard_game.start()

        board_copy = standard_game.board[:]
        cards_copy = standard_game.cards.copy()

        the_set = frozenset(
            {
                Card(Number.THREE, Color.GREEN, Shading.SOLID, Shape.OVAL),
                Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),
                Card(Number.THREE, Color.RED, Shading.EMPTY, Shape.OVAL),
            }
        )
        result = standard_game.accept_set(the_set, player="jeff")

        assert not result
        assert standard_game.board == board_copy
        assert standard_game.cards == cards_copy
        assert standard_game.players == {"ron": [], "jeff": []}

    def test_accept_set_fails_with_invalid_cards(self, standard_game):
        standard_game.add_player("ron")
        standard_game.add_player("jeff")

        standard_game.start()

        board_copy = standard_game.board[:]
        cards_copy = standard_game.cards.copy()

        the_set = frozenset(
            {
                Card(Number.ONE, Color.GREEN, Shading.EMPTY, Shape.SQUIGGLE),
                Card(Number.TWO, Color.GREEN, Shading.EMPTY, Shape.OVAL),
                # this card is not on the board
                Card(Number.THREE, Color.GREEN, Shading.EMPTY, Shape.DIAMOND),
            }
        )
        result = standard_game.accept_set(the_set, player="ron")

        assert not result
        assert standard_game.board == board_copy
        assert standard_game.cards == cards_copy
        assert standard_game.players == {"ron": [], "jeff": []}
