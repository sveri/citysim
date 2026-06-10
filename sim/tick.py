"""Tick engine — runs in a background thread, advances simulation time."""
import threading
import time
from datetime import date, timedelta
from db.schema import SessionLocal, WorldState
from sim.events.lifecycle import process_lifecycle

WEEK = timedelta(weeks=1)

# Subscribers receive lists of event dicts from each tick
_subscribers: list = []
_subscribers_lock = threading.Lock()
_sim_thread: threading.Thread | None = None
_stop_event = threading.Event()


def subscribe(callback):
    with _subscribers_lock:
        _subscribers.append(callback)


def unsubscribe(callback):
    with _subscribers_lock:
        _subscribers.discard(callback) if hasattr(_subscribers, "discard") else None
        try:
            _subscribers.remove(callback)
        except ValueError:
            pass


def _notify(tick: int, sim_date: str, events: list):
    with _subscribers_lock:
        cbs = list(_subscribers)
    for cb in cbs:
        try:
            cb(tick, sim_date, events)
        except Exception:
            pass


def advance_one_tick(session) -> tuple[int, str, list]:
    world = session.query(WorldState).first()
    sim_date = date.fromisoformat(world.sim_date) + WEEK
    world.sim_date = sim_date.isoformat()
    world.tick += 1
    session.commit()

    events = process_lifecycle(session, sim_date)
    return world.tick, world.sim_date, events


def _run_loop():
    while not _stop_event.is_set():
        speed_ms = 100  # default; overwritten when running

        try:
            with SessionLocal() as session:
                world = session.query(WorldState).first()
                if not world or not world.running:
                    _stop_event.wait(0.1)
                    continue
                speed_ms = world.tick_speed_ms

            with SessionLocal() as session:
                tick, sim_date, events = advance_one_tick(session)

            _notify(tick, sim_date, events)
        except Exception:
            import traceback
            traceback.print_exc()

        _stop_event.wait(speed_ms / 1000)


def start_engine():
    global _sim_thread
    _stop_event.clear()
    _sim_thread = threading.Thread(target=_run_loop, daemon=True)
    _sim_thread.start()


def stop_engine():
    _stop_event.set()


def set_running(running: bool):
    session = SessionLocal()
    try:
        world = session.query(WorldState).first()
        if world:
            world.running = running
            session.commit()
    finally:
        session.close()


def set_speed(ms: int):
    session = SessionLocal()
    try:
        world = session.query(WorldState).first()
        if world:
            world.tick_speed_ms = max(100, min(ms, 10000))
            session.commit()
    finally:
        session.close()
