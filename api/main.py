import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import state, control, build
from api import ws as ws_hub

app = FastAPI(title="CitySim")

app.include_router(state.router)
app.include_router(control.router)
app.include_router(build.router)

app.mount("/ui", StaticFiles(directory="ui"), name="ui")


@app.get("/")
def root():
    return FileResponse("ui/index.html")


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await ws_hub.websocket_endpoint(websocket)


@app.on_event("startup")
async def startup():
    ws_hub.set_loop(asyncio.get_event_loop())
