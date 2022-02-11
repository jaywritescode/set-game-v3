from itertools import product
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
    test_game.cards = shuffled_deck[:]
    return test_game

@pytest.fixture
def large_game(needs_extra_cards, test_game):
    """
    No Sets in the first sixteen cards drawn, so we need to draw eighteen to start.
    """
    test_game.cards = needs_extra_cards[:]
    return test_game

@pytest.fixture
def largest_game(deals_extra_cards_after_first_set, test_game):
    """
    The first three cards drawn form a Set, but then there's no Set in the following
    twenty cards. Any twenty-one cards is guaranteed to have at least one Set.
    """
    test_game.cards = deals_extra_cards_after_first_set[:]
    return test_game

class TestGame:
    def test_start_with_at_least_one_set_in_first_twelve_cards(self, standard_game):
        standard_game.start()

        assert len(standard_game.board) == 12
        assert len(standard_game.board) + len(standard_game.cards) == 81

    def test_start_with_no_sets_in_the_first_twelve_cards(self, large_game):
        large_game.start()

        assert len(large_game.board) == 18
        assert len(large_game.board) + len(large_game.cards) == 81

    def test_add_player_game_not_started(self, standard_game):
        standard_game.add_player('ron')
        standard_game.add_player('jeff')

        assert standard_game.players == {
            'ron': [],
            'jeff': []
        }

    def test_add_player_cannot_add_duplicate_player(self, standard_game):
        standard_game.add_player('ron')
        standard_game.add_player('jeff')
        
        with pytest.raises(ValueError):
            standard_game.add_player('ron')

        assert standard_game.players == {
            'ron': [],
            'jeff': []
        }        

    def test_accept_set_with_valid_set(self, standard_game):
        standard_game.start()

        standard_game.add_player('ron')
        standard_game.add_player('jeff')

        the_set = frozenset({ 
            Card(Number.THREE, Color.GREEN, Shading.SOLID, Shape.OVAL),
            Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),
            Card(Number.TWO, Color.BLUE, Shading.STRIPED, Shape.DIAMOND)
        })
        result = standard_game.accept_set(the_set, player='ron')

        assert result
        for card in the_set:
            assert card not in standard_game.board
        assert len(standard_game.board) == 12
        assert len(standard_game.board) + len(standard_game.cards) == 78
        assert standard_game.players == {
            'ron': [the_set],
            'jeff': []
        }

    def test_accept_set_with_valid_set_then_no_sets_in_next_twenty_cards(self, largest_game):
        largest_game.add_player('ron')
        largest_game.add_player('jeff')

        largest_game.start()

        the_set = frozenset({
            Card(Number.TWO, Color.BLUE, Shading.SOLID, Shape.OVAL),
            Card(Number.TWO, Color.BLUE, Shading.EMPTY, Shape.OVAL),
            Card(Number.TWO, Color.BLUE, Shading.STRIPED, Shape.OVAL),
        })
        result = largest_game.accept_set(the_set, player="jeff")

        assert result
        for card in the_set:
            assert card not in largest_game.board
        assert len(largest_game.board) == 21
        assert len(largest_game.board) + len(largest_game.cards) == 78
        assert largest_game.players == {
            'ron': [],
            'jeff': [the_set]
        }

    def test_accept_set_fails_with_invalid_set(self, standard_game):
        standard_game.add_player('ron')
        standard_game.add_player('jeff')

        standard_game.start()

        board_copy = standard_game.board[:]
        cards_copy = standard_game.cards.copy()

        the_set = frozenset({
            Card(Number.THREE, Color.GREEN, Shading.SOLID, Shape.OVAL),
            Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),
            Card(Number.THREE, Color.RED, Shading.EMPTY, Shape.OVAL)
        })
        result = standard_game.accept_set(the_set, player="jeff")

        assert not result
        assert standard_game.board == board_copy
        assert standard_game.cards == cards_copy
        assert standard_game.players == {
            'ron': [],
            'jeff': []
        }

    def test_accept_set_fails_with_invalid_cards(self, standard_game):
        standard_game.add_player("ron")
        standard_game.add_player("jeff")
        
        standard_game.start()

        board_copy = standard_game.board[:]
        cards_copy = standard_game.cards.copy()

        the_set = frozenset({
            Card(Number.ONE, Color.GREEN, Shading.EMPTY, Shape.SQUIGGLE),
            Card(Number.TWO, Color.GREEN, Shading.EMPTY, Shape.OVAL),
            # this card is not on the board
            Card(Number.THREE, Color.GREEN, Shading.EMPTY, Shape.DIAMOND)
        })
        result = standard_game.accept_set(the_set, player="ron")

        assert not result
        assert standard_game.board == board_copy
        assert standard_game.cards == cards_copy
        assert standard_game.players == {
            'ron': [],
            'jeff': []
        }