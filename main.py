import uvicorn
from sim.world import seed_world
from sim import tick as engine


if __name__ == "__main__":
    seed_world()
    engine.start_engine()

    from api.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
