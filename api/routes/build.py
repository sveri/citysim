from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.schema import SessionLocal, Plot

router = APIRouter(prefix="/api/build")


class RoadRequest(BaseModel):
    x: int
    y: int


@router.post("/road")
def build_road(req: RoadRequest):
    session = SessionLocal()
    try:
        plot = session.query(Plot).filter_by(x=req.x, y=req.y).first()
        if not plot:
            raise HTTPException(status_code=404, detail="Plot not found")
        if plot.terrain == "river":
            raise HTTPException(status_code=400, detail="Cannot build road on river")
        if plot.households:
            raise HTTPException(status_code=400, detail="Plot is occupied by a household")
        plot.terrain = "road"
        session.commit()
        return {"x": req.x, "y": req.y, "terrain": "road"}
    finally:
        session.close()


@router.delete("/road")
def remove_road(req: RoadRequest):
    session = SessionLocal()
    try:
        plot = session.query(Plot).filter_by(x=req.x, y=req.y).first()
        if not plot:
            raise HTTPException(status_code=404, detail="Plot not found")
        if plot.terrain != "road":
            raise HTTPException(status_code=400, detail="Plot is not a road")
        plot.terrain = "grass"
        session.commit()
        return {"x": req.x, "y": req.y, "terrain": "grass"}
    finally:
        session.close()
