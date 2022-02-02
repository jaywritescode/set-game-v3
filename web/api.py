import json
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from setgame.setgame import Game, deck
from web.serialize import BoardSchema

game = Game()

templates = Jinja2Templates(directory='templates', extensions=['jinja2.ext.debug'])

board_schema = BoardSchema()

async def index(request):
    return templates.TemplateResponse('index.html.jinja', {
        'deck': deck(),
        'request': request 
    })

class Echo(WebSocketEndpoint):
    encoding = "text"

    async def on_connect(self, websocket):
        await websocket.accept()
    
    async def on_receive(self, websocket, data):
        actions = {
            'init': self.do_init,
            'start': self.do_start,
        }

        args = json.loads(data)
        action_type = args['type']
        if action_type not in actions.keys():
            # error handling
            pass

        response = actions[action_type]()
        response.update({ 'type': action_type })

        await websocket.send_json(response)
    
    async def on_disconnect(self, websocket, close_code):
        pass

    def do_init(self):
        return board_schema.dump(game)

    def do_start(self):
        game.start()
        return board_schema.dump(game)


app = Starlette(debug=True, routes=[
    Route('/', index), 
    WebSocketRoute('/', Echo),
    Mount('/static', StaticFiles(directory='static'), name="static")
])