from collections import deque
from dataclasses import dataclass, fields
from enum import Enum
from itertools import combinations, product
import random

Number = Enum('Number', 'ONE TWO THREE', start=0)

Color = Enum('Color', 'RED BLUE GREEN', start=0)

Shading = Enum('Shading', 'EMPTY SOLID STRIPED', start=0)

Shape = Enum('Shape', 'DIAMOND OVAL SQUIGGLE', start=0)

@dataclass(frozen=True)
class Card:
    number: Number
    color: Color
    shading: Shading
    shape: Shape

    def index(self):
        return sum(getattr(self, field.name).value * (3 ** i) for (i, field) in enumerate(fields(Card)))

def is_set(cards):
    if len(cards) != 3:
        return False

    for field in fields(Card):
        if not sum(getattr(card, field.name).value for card in cards) % 3 == 0:
            return False
    return True

def complete_set(c, d):
    number = Number(-(c.number.value + d.number.value) % 3)
    color = Color(-(c.color.value + d.color.value) % 3)
    shading = Shading(-(c.shading.value + d.shading.value) % 3)
    shape = Shape(-(c.shape.value + d.shape.value) % 3)
    return Card(number, color, shading, shape)

def contains_set(cards):
    """
    Determines if there's at least one Set in the given collection of Cards.
    """
    return any(complete_set(*pair) in cards for pair in combinations(cards, 2))

def find_set(cards):
    for pair in combinations(cards, 2):
        k = complete_set(*pair)
        if k in cards:
            return (pair[0], pair[1], k)

def deck():
    return [Card(*attrs) for attrs in product(Number, Color, Shading, Shape)]


class Game:
    def __init__(self, shuffler=random.shuffle, seed=None):
        self.shuffler = shuffler
        if seed is not None:
            random.seed(seed)

        self.reset()

    def reset(self):
        self.cards = deque(deck())
        self.board = []
        self.players = dict()

    def start(self):
        if self.is_started():
            return
        
        self.shuffle()
        self.deal()

    def shuffle(self):
        self.shuffler(self.cards)
        self.cards = deque(self.cards)

    def deal(self):
        while len(self.board) < 12 or not self.has_set():
            if not self.cards:
                return False

            for _ in range(3):
                self.board.append(self.cards.popleft())

        # True means there are at least twelve cards and at least one set on the board.
        return True

    def add_player(self, name):
        if name in self.players:
            raise ValueError(f"{name} is already playing.")

        self.players[name] = list()

    def accept_set(self, cards, *, player):
        """Takes a set, submitted by player, and updates the game state.

        :param cards: a collection of cards
        :param player: the player name
        :return: True if the set is valid, otherwise False
        """
        if not all(card in self.board for card in cards):
            return False

        if not is_set(cards):
            return False

        for card in cards:
            self.board.remove(card)

        self.players[player].append(cards)
        
        self.deal()
        return True

    def has_set(self):
        return contains_set(self.board)

    def is_started(self):
        return self.board


if __name__ == '__main__':
    import marshmallow_dataclass
    from pprint import pprint
    
    deck = deck()

    capset = [
        Card(Number.ONE, Color.GREEN, Shading.EMPTY, Shape.DIAMOND),
        Card(Number.ONE, Color.GREEN, Shading.SOLID, Shape.DIAMOND),
        Card(Number.ONE, Color.RED, Shading.STRIPED, Shape.DIAMOND),
        Card(Number.ONE, Color.BLUE, Shading.STRIPED, Shape.SQUIGGLE),
        Card(Number.ONE, Color.RED, Shading.EMPTY, Shape.SQUIGGLE),
        Card(Number.ONE, Color.RED, Shading.SOLID, Shape.SQUIGGLE),
        Card(Number.ONE, Color.GREEN, Shading.EMPTY, Shape.OVAL),
        Card(Number.ONE, Color.GREEN, Shading.SOLID, Shape.OVAL),
        Card(Number.ONE, Color.RED, Shading.STRIPED, Shape.OVAL),
        Card(Number.TWO, Color.GREEN, Shading.STRIPED, Shape.SQUIGGLE),
        Card(Number.TWO, Color.RED, Shading.STRIPED, Shape.SQUIGGLE),
        Card(Number.THREE, Color.GREEN, Shading.STRIPED, Shape.DIAMOND),
        Card(Number.THREE, Color.RED, Shading.EMPTY, Shape.DIAMOND),
        Card(Number.THREE, Color.RED, Shading.SOLID, Shape.DIAMOND),
        Card(Number.THREE, Color.GREEN, Shading.EMPTY, Shape.SQUIGGLE),
        Card(Number.THREE, Color.GREEN, Shading.SOLID, Shape.SQUIGGLE),
        Card(Number.THREE, Color.BLUE, Shading.STRIPED, Shape.SQUIGGLE),
        Card(Number.THREE, Color.GREEN, Shading.STRIPED, Shape.OVAL),
        Card(Number.THREE, Color.RED, Shading.EMPTY, Shape.OVAL),
        Card(Number.THREE, Color.RED, Shading.SOLID, Shape.OVAL)
    ]
    set = [
        Card(Number.TWO, Color.BLUE, Shading.SOLID, Shape.OVAL),
        Card(Number.TWO, Color.BLUE, Shading.EMPTY, Shape.OVAL),
        Card(Number.TWO, Color.BLUE, Shading.STRIPED, Shape.OVAL),
    ]

    for card in capset + set:
        deck.remove(card)
    

    CardSchema = marshmallow_dataclass.class_schema(Card)()

    print(CardSchema.dumps(set + capset + deck, many=True))