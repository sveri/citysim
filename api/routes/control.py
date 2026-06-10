from fastapi import APIRouter
from pydantic import BaseModel
from sim import tick as engine
from db.schema import SessionLocal, WorldState
from sim.events.lifecycle import age_of
from datetime import date

router = APIRouter(prefix="/api")


class SpeedRequest(BaseModel):
    ms: int


@router.post("/sim/start")
def sim_start():
    engine.set_running(True)
    return {"status": "running"}


@router.post("/sim/pause")
def sim_pause():
    engine.set_running(False)
    return {"status": "paused"}


@router.post("/sim/tick")
def sim_single_tick():
    session = SessionLocal()
    try:
        tick, sim_date, events = engine.advance_one_tick(session)
        engine._notify(tick, sim_date, events)
        return {"tick": tick, "sim_date": sim_date, "events": events}
    finally:
        session.close()


@router.post("/sim/speed")
def sim_speed(req: SpeedRequest):
    engine.set_speed(req.ms)
    return {"tick_speed_ms": req.ms}
