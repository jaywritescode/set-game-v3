from collections import deque
from dataclasses import dataclass
from enum import Enum
from itertools import product
from random import shuffle

Number = Enum('Number', 'ONE TWO THREE')

Color = Enum('Color', 'RED BLUE GREEN')

Shading = Enum('Shading', 'EMPTY SOLID STRIPED')

Shape = Enum('Shape', 'DIAMOND OVAL SQUIGGLE')

@dataclass(frozen=True)
class Card:
    number: Number
    color: Color
    shading: Shading
    shape: Shape


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.cards = [Card(*attrs) for attrs in product(Number, Color, Shading, Shape)]
        self.board = []

    def start(self):
        shuffle(self.cards)
        self.cards = deque(self.cards)
        for _ in range(12):
            self.board.append(self.cards.popleft())


if __name__ == '__main__':
    g = Game()
    for c in g.cards:
        print(c)