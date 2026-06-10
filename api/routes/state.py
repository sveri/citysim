from fastapi import APIRouter
from db.schema import SessionLocal, WorldState, Plot, Household, Person
from sim.events.lifecycle import age_of
from datetime import date

router = APIRouter(prefix="/api")


@router.get("/state")
def get_state():
    session = SessionLocal()
    try:
        world = session.query(WorldState).first()
        plots = session.query(Plot).all()
        households = session.query(Household).all()
        people = session.query(Person).all()

        sim_date = date.fromisoformat(world.sim_date)

        plots_data = [
            {"id": p.id, "x": p.x, "y": p.y, "terrain": p.terrain,
             "household_id": p.households[0].id if p.households else None}
            for p in plots
        ]

        households_data = [
            {
                "id": h.id,
                "plot_id": h.plot_id,
                "members": [
                    {
                        "id": m.id,
                        "name": f"{m.first_name} {m.last_name}",
                        "sex": m.sex,
                        "age": age_of(m.birth_date, sim_date),
                        "alive": m.alive,
                    }
                    for m in h.members
                ]
            }
            for h in households
        ]

        return {
            "tick": world.tick,
            "sim_date": world.sim_date,
            "running": world.running,
            "tick_speed_ms": world.tick_speed_ms,
            "plots": plots_data,
            "households": households_data,
        }
    finally:
        session.close()
