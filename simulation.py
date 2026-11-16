import heapq
from recovery.manager import RecoveryManager
from classes import Event, SimulationState
from metrics import SimulationMetrics
from events import process_event

def build_event_queue(fleet):

    events = []

    for plane in fleet.values():

        if not plane.assigned_flights:
            continue

        first_flight = plane.assigned_flights[0]

        heapq.heappush(events, Event(time=first_flight.scheduled_departure, event_type="Departure", flight=first_flight))

    return events

def run_simulation(schedule, fleet, config, simulation_seed, airports=None):
    state = SimulationState(
        flights=schedule,
        fleet=fleet,
        events=[],
        metrics=SimulationMetrics(),
        config=config,
        recovery_manager=RecoveryManager(config.recovery_strategy),
        simulation_seed=simulation_seed,
        airports=airports,
    )

    reset_simulation(state)
    state.events.extend(build_event_queue(state.fleet))

    while state.events:
        event = heapq.heappop(state.events)
        process_event(event, state)
        
    return state.metrics

def reset_simulation(state):

    for flight in state.flights:
        flight.reset()

    for plane in state.fleet.values():
        plane.reset(state.config)

    state.events.clear()
    state.metrics.reset()
    state.metrics.total_flights = len(state.flights)