from marshmallow import Schema, fields
import marshmallow_dataclass

from setgame.setgame import Card


CardSchema = marshmallow_dataclass.class_schema(Card)()


class GameSchema(Schema):
    board = fields.List(fields.Nested(CardSchema))
    players = fields.Dict(
        keys=fields.Str(), values=fields.List(fields.List(fields.Nested(CardSchema)))
    )
    game_over = fields.Boolean()
