"""WebSocket hub — broadcasts tick events to all connected browsers."""
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from sim import tick as engine

_connections: set[WebSocket] = set()
_loop: asyncio.AbstractEventLoop | None = None


def set_loop(loop: asyncio.AbstractEventLoop):
    global _loop
    _loop = loop
    engine.subscribe(_on_tick)


def _on_tick(tick: int, sim_date: str, events: list):
    if not _loop or not _connections:
        return
    payload = json.dumps({"tick": tick, "sim_date": sim_date, "events": events})
    asyncio.run_coroutine_threadsafe(_broadcast(payload), _loop)


async def _broadcast(payload: str):
    dead = set()
    for ws in list(_connections):
        try:
            await ws.send_text(payload)
        except Exception:
            dead.add(ws)
    _connections.difference_update(dead)


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive; client sends nothing
    except WebSocketDisconnect:
        _connections.discard(websocket)
