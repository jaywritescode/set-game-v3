import marshmallow_dataclass
import os
import pytest
from starlette.testclient import TestClient

from setgame.setgame import Card
from web.api import app

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

CardSchema = marshmallow_dataclass.class_schema(Card)()


@pytest.fixture
def shuffled_deck():
    with open(os.path.join(FIXTURE_DIR, "deck1.txt")) as file:
        return CardSchema.loads(file.read(), many=True)


@pytest.fixture
def needs_extra_cards():
    with open(os.path.join(FIXTURE_DIR, "deck2.txt")) as file:
        return CardSchema.loads(file.read(), many=True)


@pytest.fixture
def deals_extra_cards_after_first_set():
    with open(os.path.join(FIXTURE_DIR, "deck3.txt")) as file:
        return CardSchema.loads(file.read(), many=True)


# @pytest.fixture(scope="module")
# def test_app():
#     client = TestClient(app)
#     yield client
