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


class SetGameApi(WebSocketEndpoint):
    encoding = "text"

    def __init__(self, scope, receive, send):
        super().__init__(scope, receive=receive, send=send)
        self.state().connections = ConnectionManager()

    # fix the getter so that self.state points to self.app.state
    def state(self):
        return self.scope['app'].state

    def connections(self):
        return self.state().connections

    async def on_connect(self, websocket):
        await self.connections().accept(websocket)
    
    async def on_receive(self, websocket, data):
        actions = {
            'init': self.do_init,
            'start': self.do_start,
            'submit': self.do_submit,
        }

        try:
            args = json.loads(data)
        except:
            await websocket.send_text('not json')
            return

        action_type = args['type']
        if action_type not in actions.keys():
            # error handling
            pass

        response = actions[action_type](**args)
        response.update(args)

        await websocket.send_json(response)
          
    async def on_disconnect(self, websocket, close_code):
        await super().on_disconnect(websocket, close_code)
        self.connections().disconnect(websocket)

    def do_init(self, **kwargs):
        if not getattr(self.state(), 'game', None):
            self.state().game = Game()

        return game_schema.dump(self.state().game)

    def do_start(self, state, **kwargs):
        # TODO: getattr(state, 'game') should not throw here
        if not state.game.is_started():
            state.game.start()    
            return game_schema.dump(state.game)

    def do_submit(self, state, **kwargs):
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
