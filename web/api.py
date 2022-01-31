import json
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute

from setgame.setgame import Game
from web.serialize import BoardSchema

game = Game()

board_schema = BoardSchema()

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


app = Starlette(debug=True, routes=[WebSocketRoute('/', Echo)])