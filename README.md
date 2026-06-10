# CitySim

Realistic German city simulation. Build a city from scratch on flat terrain near a river. Simulation runs in the background; a web UI updates live via WebSocket.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (package manager)

Install uv if not already present:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

```bash
git clone https://github.com/sveri/citysim.git
cd citysim
uv sync
```

## Run

```bash
uv run python main.py
```

Open **http://localhost:8000** in your browser.

The simulation starts paused. Use the controls in the sidebar:

| Control | Action |
|---|---|
| ▶ Start | Run simulation continuously |
| ⏸ Pause | Pause simulation |
| ▶\| Step | Advance one tick (= 1 week) |
| Speed slider | Set tick interval (100ms – 5000ms) |

Click any plot on the map to see its details and available actions (build/remove road).

## State

Simulation state is persisted in `citysim.db` (SQLite). Delete it to reset the world:

```bash
rm citysim.db
uv run python main.py
```

## Project layout

```
sim/          simulation engine (tick loop, lifecycle events)
db/           SQLAlchemy models, SQLite schema
api/          FastAPI app, REST routes, WebSocket hub
ui/           single-file browser UI (no build step)
main.py       entry point
```
