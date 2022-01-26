from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute

from setgame.setgame import Game
from web.serialize import BoardSchema

class Echo(WebSocketEndpoint):
    encoding = "text"
    async def on_connect(self, websocket):
        await websocket.accept()
    async def on_receive(self, websocket, data):
        await websocket.send_text(f"Message text was: {data}")
    async def on_disconnect(self, websocket, close_code):
        pass


app = Starlette(debug=True, routes=[WebSocketRoute('/', Echo)])