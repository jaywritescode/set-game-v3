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

class Api(WebSocketEndpoint):
    encoding = "text"

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

        response = actions[action_type](self, **args)
        response.update({ 'type': action_type })

        await websocket.send_json(response)
          
    async def on_disconnect(self, websocket, close_code):
        return await super().on_disconnect(websocket, close_code)

    def do_init(self, **kwargs):
        if self.game is None:
            return dict()

        return board_schema.dump(self.game)

    def do_start(self, **kwargs):
        if self.game is None:
            self.game = Game()
            self.game.start()
        
        return board_schema.dump(self.game)

    def do_submit(self, **kwargs):
        cards = kwargs['cards']


app = Starlette(debug=True, routes=[
    Route('/', index), 
    WebSocketRoute('/', Api),
    Mount('/build', StaticFiles(directory='build'), name="static")
])
