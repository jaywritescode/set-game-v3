from setgame import Game

class TestGame:
    def test_start(self):
        game = Game()
        game.start()

        assert len(game.board) >= 12
        assert len(game.board) + len(game.cards) == 81
