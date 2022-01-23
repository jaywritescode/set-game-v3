from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
import uvicorn

async def index(request):
    return PlainTextResponse("hello world!")

app = Starlette(debug=True, routes=[
    Route('/', index)
])


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)