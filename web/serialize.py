from marshmallow import Schema, fields, pre_load
import marshmallow_dataclass
from marshmallow_enum import EnumField

from setgame.setgame import Card


CardSchema = marshmallow_dataclass.class_schema(Card)()

class BoardSchema(Schema):
    board = fields.List(fields.Str())