# Airline Operations Recovery Simulator

A coordinated airline operations project with three independently runnable parts: a flight scheduler, a disruption and recovery simulator, and an analytics dashboard.

Live dashboard: https://airline-recovery-simulator.streamlit.app/

## The Three Parts

### 1. Schedule Generator

Builds multi-day aircraft rotations from the airport, aircraft, and route data in `data/`. Reserve aircraft are held out of planned rotations for recovery use.

```powershell
python scheduler.py
```

Writes `results/schedule.csv`.

### 2. Recovery Simulation

Runs seeded Monte Carlo experiments with weather, gate, and maintenance disruptions. Each seed uses the same generated schedule and per-flight disruption draws under `none`, `activateReserve`, `activateReserveReposition`, `aircraftSwap`, and `cyclicalAircraftSwap` strategies, so results can be compared on a paired basis.

```powershell
python main.py
```

Writes `results/simulation_results.csv` and `results/flight_results.csv`. Reserve policies activate when connection delay reaches the configured threshold (30 minutes by default) and an unused reserve can cover the next flight by its scheduled departure. `activateReserve` requires the reserve to already be at the flight's origin; `activateReserveReposition` can instead reposition it directly from its current airport when the estimated ferry time (great-circle distance at cruise speed plus taxi buffer), followed by turnaround time, fits the available window. An activated reserve takes over that aircraft's remaining rotation, preventing that connection delay from propagating.

`aircraftSwap` exchanges the remaining rotations of two aircraft when both are at the disrupted flight's origin, the second aircraft has not departed its next flight, and both aircraft can make the other's next scheduled departure. This avoids assigning an aircraft to a flight it cannot reach, but can transfer later delays with the rotation. Recovery does not remove delay already incurred by the disrupted flight. Flight-level results identify the recovery action and assigned aircraft; summary results include reserve repositioning and aircraft swap counts.

`cyclicalAircraftSwap` searches for a feasible cycle of three or four active aircraft. It only reassigns rotations when each aircraft is already at the next flight's origin and available by that flight's current departure time. The shortest feasible cycle is selected, with aircraft tail numbers providing a deterministic tie-break. In-progress flights are not reassigned.

### 3. Analytics Dashboard

Reads the experiment CSVs and compares total and propagated delay, completed flights, reserve activations, and delay avoided by strategy. It also includes flight-level results.

```powershell
streamlit run dashboard.py
```

Run the experiment first to generate dashboard data. The dashboard will explain when those artifacts are missing or empty.

## Setup and Tests

Install runtime dependencies from the repository root:

```powershell
python -m pip install -r requirements.txt
```

## Data Flow

The scheduler reads JSON inputs and creates rotations. The simulator reuses that schedule across paired random seeds and writes summary and flight-level CSVs. The dashboard consumes those CSV artifacts; it does not run simulations itself.
