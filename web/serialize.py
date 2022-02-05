from marshmallow import Schema, fields
import marshmallow_dataclass

from setgame.setgame import Card


CardSchema = marshmallow_dataclass.class_schema(Card)()

class BoardSchema(Schema):
    board = fields.List(fields.Str())