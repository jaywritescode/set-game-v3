from collections import namedtuple
import json
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from setgame.setgame import Game, deck
from web.serialize import CardSchema, GameSchema

templates = Jinja2Templates(directory='templates', extensions=['jinja2.ext.debug'])

game_schema = GameSchema()


async def index(request):
    return templates.TemplateResponse('index.html.jinja', {
        'deck': deck(),
        'request': request 
    })

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


Message = namedtuple('Message', ['data', 'broadcast'], defaults=[False])


class SetGameApi(WebSocketEndpoint):
    encoding = "text"

    def __init__(self, scope, receive, send):
        super().__init__(scope, receive=receive, send=send)

    @property
    def state(self):
        return self.scope['app'].state

    @property
    def connections(self):
        return self.state.connections

    @property
    def game(self):
        return getattr(self.state, 'game', None)

    async def on_connect(self, websocket):
        await self.connections.accept(websocket)
    
    async def on_receive(self, websocket, data):
        actions = {
            'joinRoom': self.handle_join_room,
            'start': self.handle_start,
            'submit': self.do_submit,
        }

        args = json.loads(data)
        action_type = args['type']
        if action_type not in actions.keys():
            # error handling
            pass

        message = actions[action_type](**args['payload'])
        response = {
            'type': action_type,
            'payload': message.data
        }

        if message.broadcast:
            await self.connections.broadcast(response)
        else:
            await websocket.send_json(response)
          
    async def on_disconnect(self, websocket, close_code):
        await super().on_disconnect(websocket, close_code)
        self.connections.disconnect(websocket)

    def handle_join_room(self, **kwargs):
        if not self.game:
            self.state.game = Game()

        try:
            self.game.add_player(kwargs['playerName'])
            return Message(game_schema.dump(self.game), broadcast=True)
        except ValueError as e:
            return Message({ 'error': e.args })

    def handle_start(self, **kwargs):
        if self.game.is_started():
            return Message({ 'error': 'game is already started '})

        self.game.start()
        return Message(game_schema.dump(self.game), broadcast=True)        
        

    def do_submit(self, state, **kwargs):
        raise

        if not state.game.is_started():
            # TODO: handle error
            return dict()
        
        cards = CardSchema.load(kwargs['cards'], many=True)
        result = state.game.accept_set(cards)

        if result is None:
            # another error
            return dict()

        return game_schema.dump(state.game)


app = Starlette(debug=True, routes=[
    Route('/', index), 
    WebSocketRoute('/', SetGameApi),
    Mount('/build', StaticFiles(directory='build'), name="static")
])
app.state.connections = ConnectionManager()