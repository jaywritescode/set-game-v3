import itertools
from marshmallow.exceptions import ValidationError
import marshmallow_dataclass
import os
import pytest

from setgame.setgame import Card

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

CardSchema = marshmallow_dataclass.class_schema(Card)()

@pytest.fixture
def shuffled_deck():
    with open(os.path.join(FIXTURE_DIR, 'deck1.txt')) as file:
        return CardSchema.loads(file.read(), many=True)

@pytest.fixture
def needs_extra_cards():
    with open(os.path.join(FIXTURE_DIR, 'deck2.txt')) as file:
        return CardSchema.loads(file.read(), many=True)