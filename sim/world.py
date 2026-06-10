"""World initialisation — creates the 10×10 grid with river along y=0."""
import random
from datetime import date
from db.schema import SessionLocal, WorldState, Plot, Household, Person, init_db
from sim.events.lifecycle import GERMAN_FIRST_NAMES_M, GERMAN_FIRST_NAMES_F, GERMAN_LAST_NAMES

GRID_W = 10
GRID_H = 10
RIVER_Y = 0  # bottom row is river


def seed_world():
    init_db()
    session = SessionLocal()
    try:
        existing = session.query(WorldState).first()
        if existing:
            return  # already seeded

        world = WorldState(tick=0, sim_date="1990-01-07", running=False, tick_speed_ms=500)
        session.add(world)

        plots = {}
        for y in range(GRID_H):
            for x in range(GRID_W):
                terrain = "river" if y == RIVER_Y else "grass"
                p = Plot(x=x, y=y, terrain=terrain)
                session.add(p)
                session.flush()
                plots[(x, y)] = p

        # Seed initial road network: vertical main street (x=5, y=1..9)
        # + horizontal cross street (y=5, x=1..9), excluding household plot (5,5)
        for y in range(1, GRID_H):
            plots[(5, y)].terrain = "road"
        for x in range(1, GRID_W):
            plots[(x, 5)].terrain = "road"

        # Place one founding household on plot (6, 6) — grass, adjacent to road cross
        start_plot = plots[(6, 6)]
        last_name = random.choice(GERMAN_LAST_NAMES)
        household = Household(plot_id=start_plot.id)
        session.add(household)
        session.flush()

        # Couple: man ~32, woman ~29, married in 1985
        members = [
            Person(household_id=household.id, first_name=random.choice(GERMAN_FIRST_NAMES_M),
                   last_name=last_name, sex="M", birth_date="1957-03-15", alive=True),
            Person(household_id=household.id, first_name=random.choice(GERMAN_FIRST_NAMES_F),
                   last_name=last_name, sex="F", birth_date="1960-08-22", alive=True),
        ]
        for m in members:
            session.add(m)

        session.commit()
        print(f"World seeded. Founding family: {last_name}")
    finally:
        session.close()
