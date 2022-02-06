from collections import deque
from dataclasses import dataclass, fields
from enum import Enum
from itertools import combinations, product
from random import shuffle

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

    def __str__(self):
        return '-'.join(e.name for e in [self.number, self.color, self.shading, self.shape]).lower()


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
    def __init__(self, shuffler=shuffle):
        self.reset()
        self.shuffler = shuffler

    def reset(self):
        self.cards = deck()
        self.board = []

    def start(self):
        if self.is_started():
            return

        self.shuffler(self.cards)
        self.cards = deque(self.cards)
        
        self.deal()

    def deal(self):
        while len(self.board) < 12 or not self.has_set():
            if not self.cards:
                # no more cards, game over
                return True

            for _ in range(3):
                self.board.append(self.cards.popleft())

    def accept_set(self, cards):
        if not all(card in self.board for card in cards):
            return None

        if not is_set(cards):
            return None

        for card in cards:
            self.board.remove(card)
        
        self.deal()
        return self.board

    def has_set(self):
        return contains_set(self.board)

    def is_started(self):
        return self.board


if __name__ == '__main__':
    import marshmallow_dataclass
    from pprint import pprint
    
    deck = deck()
    shuffle(deck)

    CardSchema = marshmallow_dataclass.class_schema(Card)()

    s = find_set(deck[:12])
    if s:
        # pprint(CardSchema.dump(s))
        # print("=============================================")
        print(CardSchema.dumps(deck, many=True))
    else:
        print("Try again")