import heapq
import random

from classes import Event
from metrics import SimulationMetrics
from events import process_event

def build_event_queue(fleet):

    events = []

    for plane in fleet.values():

        if not plane.remaining_flights:
            continue

        first_flight = plane.remaining_flights[0]

        heapq.heappush(events, Event(time=first_flight.scheduled_departure, event_type="Departure", flight=first_flight))

    return events

def run_simulation(schedule, fleet, routes, config, simulation_seed):
    random.seed(simulation_seed)
    reset_simulation(schedule, fleet, routes, config)

    metrics = SimulationMetrics()
    metrics.total_flights = len(schedule)
    
    events = build_event_queue(fleet)

    while events:
        event = heapq.heappop(events)
        process_event(event, fleet, events, config, metrics)
        
    return metrics

def reset_simulation(schedule, fleet, routes, config):

    for flight in schedule:
        flight.reset()

    for plane in fleet.values():
        plane.reset(config)

    for route in routes.values():
        route.reset()
    