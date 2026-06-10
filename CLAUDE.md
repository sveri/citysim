# CitySim

## Goal

Simulate building a city from scratch, as realistically as possible.

**Setting:** Flat terrain in Germany, adjacent to a river. No existing infrastructure — greenfield.

## Vision

The simulation runs continuously in the background and drives a web UI that reflects current state in (near) real time.

Realism is the north star:
- Demographics: births, deaths, migration, age cohorts
- Economy: jobs, wages, taxation, businesses, supply/demand
- Infrastructure: roads, utilities (water, power, sewage), public transit
- Housing: zoning, construction timelines, cost of living, vacancies
- Governance: municipal budget, planning decisions, elections
- Environment: river dynamics, flooding risk, green space, pollution
- Time: simulation advances in discrete ticks (configurable speed), each tick represents real-world time (e.g. one day or one week)

## Architecture (target)

- **Simulation engine** — headless background process, owns all state, advances ticks
- **State store** — persisted simulation state (DB or structured files)
- **API layer** — exposes current state and accepts player/admin commands
- **Web UI** — browser-based, reads from API, updates live (WebSocket or polling)

## Constraints

- Germany-specific rules where relevant: building codes, zoning law (BauGB/BauNVO), tax structure (Gewerbesteuer, Grundsteuer), social systems
- Simulation must be pausable, saveable, and resumable
- UI must work without build step for rapid iteration (or use a lightweight bundler)

## Non-goals (for now)

- 3D graphics / game engine
- Multiplayer
- Mobile app
