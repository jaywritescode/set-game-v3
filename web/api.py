import json
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from setgame.setgame import Game, deck
from web.serialize import BoardSchema

templates = Jinja2Templates(directory='templates', extensions=['jinja2.ext.debug'])

board_schema = BoardSchema()

async def index(request):
    return templates.TemplateResponse('index.html.jinja', {
        'deck': deck(),
        'request': request 
    })

class App(WebSocketEndpoint):
    encoding = "text"

    def __init__(self, scope, receive, send):
        super().__init__(scope, receive=receive, send=send)

    async def on_connect(self, websocket):
        await websocket.accept()
    
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

        state = websocket.app.state

        response = actions[action_type](state, **args)
        response.update({ 'type': action_type })

        await websocket.send_json(response)
          
    async def on_disconnect(self, websocket, close_code):
        return await super().on_disconnect(websocket, close_code)

    def do_init(self, state, **kwargs):
        if not getattr(state, 'game', None):
            state.game = Game()

        return board_schema.dump(state.game)

    def do_start(self, state, **kwargs):
        if not state.game.is_started():
            state.game.start()    
            return board_schema.dump(state.game)

    def do_submit(self, **kwargs):
        cards = kwargs['cards']


app = Starlette(debug=True, routes=[
    Route('/', index), 
    WebSocketRoute('/', App),
    Mount('/build', StaticFiles(directory='build'), name="static")
])
