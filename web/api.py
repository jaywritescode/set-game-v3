from collections import namedtuple
import json
import logging
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from setgame.setgame import Game, deck, find_set
from web.serialize import CardSchema, GameSchema

templates = Jinja2Templates(directory="templates", extensions=["jinja2.ext.debug"])

game_schema = GameSchema()


async def index(request):
    random_seed = request.query_params.get("seed")
    if random_seed is not None:
        request.app.state.seed = random_seed

    return templates.TemplateResponse(
        "index.html.jinja", {"deck": deck(), "request": request}
    )


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def accept(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)


Message = namedtuple("Message", ["data", "broadcast"], defaults=[False])


class SetGameApi(WebSocketEndpoint):
    encoding = "text"

    def __init__(self, scope, receive, send):
        super().__init__(scope, receive=receive, send=send)
        self.state.game = None

    @property
    def state(self):
        return self.scope["app"].state

    @property
    def connections(self):
        return self.state.connections

    @property
    def game(self):
        return self.state.game

    def create_game(self):
        if self.game is None:
            self.state.game = Game()

    async def on_connect(self, websocket):
        if 'seed' in websocket.query_params:
            self.state.seed = int(websocket.query_params['seed'])
        await self.connections.accept(websocket)

    async def on_receive(self, websocket, data):
        actions = {
            "enterRoom": self.handle_enter_room,
            "start": self.handle_start,
            "submit": self.handle_submit,
            "find_set": self.handle_find_set,
        }

        args = json.loads(data)
        action_type = args["type"]
        if action_type not in actions.keys():
            # error handling
            raise ValueError("invalid action type: " + action_type)

        message = actions[action_type](**args["payload"])
        response = {"type": action_type, "payload": message.data}

        if message.broadcast:
            await self.connections.broadcast(response)
        else:
            await websocket.send_json(response)

    async def on_disconnect(self, websocket, close_code):
        await super().on_disconnect(websocket, close_code)
        self.connections.disconnect(websocket)

    def handle_enter_room(self, **kwargs):
        if self.game is None:
            self.create_game()

        try:
            self.game.add_player(kwargs["playerName"])
            return Message(game_schema.dump(self.game), broadcast=True)
        except ValueError as e:
            return Message({"error": e.args})

    # def handle_enter_room1(self, **kwargs):
    #     print(kwargs)

    #     """Upon the user entering the room, we need to get the game state."""
    #     if not self.game:
    #         self.state.game = Game(seed=getattr(self.state, "seed", None))

    #     return Message(game_schema.dump(self.game))

    # def handle_join_room(self, **kwargs):
    #     try:
    #         self.game.add_player(kwargs["playerName"])
    #         return Message(game_schema.dump(self.game), broadcast=True)
    #     except ValueError as e:
    #         return Message({"error": e.args})

    def handle_start(self, **kwargs):
        if self.game.is_started():
            return Message({"error": "game is already started"})

        self.game.start()
        return Message(game_schema.dump(self.game), broadcast=True)

    def handle_submit(self, **kwargs):
        if not self.game.is_started():
            raise

        cards = CardSchema.load(kwargs["cards"], many=True)
        result = self.game.accept_set(cards, player=kwargs["player"])

        if not result:
            return Message({"error": "invalid"})

        return Message(game_schema.dump(self.game), broadcast=True)

    def handle_find_set(self, **kwargs):
        return Message(CardSchema.dump(find_set(self.game.board), many=True))


app = Starlette(
    debug=True,
    routes=[
        Route("/", index),
        WebSocketRoute("/ws", SetGameApi),
        Mount("/assets", StaticFiles(directory="assets"), name="static"),
    ],
)
app.state.connections = ConnectionManager()
