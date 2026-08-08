import heapq
import random

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

def run_simulation(schedule, fleet, routes, config, simulation_seed):
    random.seed(simulation_seed)
    reset_simulation(schedule, fleet, routes, config)

    metrics = SimulationMetrics()
    metrics.total_flights = len(schedule)
    
    events = build_event_queue(fleet)

    recovery = RecoveryManager(config.recovery_strategy)
    state = SimulationState(schedule, fleet, events, metrics, config, recovery)
        
    while state.events:
        event = heapq.heappop(events)
        process_event(event, state)
        
    return metrics

def reset_simulation(schedule, fleet, routes, config):

    for flight in schedule:
        flight.reset()

    for plane in fleet.values():
        plane.reset(config)
