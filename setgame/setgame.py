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
        return f"{self.number}, {self.color}, {self.shading}, {self.shape}"


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


class Game:
    def __init__(self, shuffler=shuffle):
        self.reset()
        self.shuffler = shuffler

    def reset(self):
        self.cards = [Card(*attrs) for attrs in product(Number, Color, Shading, Shape)]
        self.board = []

    def start(self):
        self.shuffler(self.cards)
        self.cards = deque(self.cards)
        
        for _ in range(12):
            self.board.append(self.cards.popleft())
        while not self.has_set():
            self.deal_more()

    def deal_more(self):
        while not self.has_set():
            if not self.cards:
                return True

            for _ in range(3):
                self.board.append(self.cards.popleft())

    def has_set(self):
        return contains_set(self.board)


if __name__ == '__main__':
    g = Game()
    # for c in g.cards:
    #     print(c)

    shuffle(g.cards)
    print([str(x) for x in g.cards[:12]])
    if contains_set(g.cards[:12]):
        print(find_set(g.cards[:12]))