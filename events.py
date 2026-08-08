import heapq
import random

from classes import Event, SimulationState
from helper import get_next_day_start

def process_event(event, state):

    if event.event_type == "Departure":
        process_departure(event, state)

    elif event.event_type == "Arrival":
        process_arrival(event, state)


def process_departure(event, state):

    flight = event.flight
    total_delay = 0

    # Weather delay
    if random.random() < state.config.weather_delay_probability:
        delay = random.randint(state.config.weather_delay_min, state.config.weather_delay_max)

        flight.weather_delay += delay
        total_delay += delay
        state.metrics.add_delay("weather", delay)

    # Gate delay
    if random.random() < state.config.gate_delay_probability:
        delay = random.randint(state.config.gate_delay_min, state.config.gate_delay_max)

        flight.gate_delay += delay
        total_delay += delay
        state.metrics.add_delay("gate", delay)

    # Maintenance delay
    if random.random() < state.config.maintenance_probability:
        delay = random.randint(state.config.maintenance_delay_min, state.config.maintenance_delay_max)

        flight.maintenance_delay += delay
        total_delay += delay
        state.metrics.add_delay("maintenance", delay)

    # Update actual times
    flight.actual_departure += total_delay
    flight.actual_arrival += total_delay

    # Recovery
    if total_delay > 0:
        state.recovery_manager.recover(event, total_delay, state)

    flight.status = "Departed"
    
    heapq.heappush(state.events, Event(time=flight.actual_arrival, event_type="Arrival", flight=flight))

def process_arrival(event, state):

    flight = event.flight
    plane = state.fleet[flight.aircraft_id]

    plane.current_airport = flight.destination
    plane.available_time = flight.actual_arrival + state.config.turn_time

    flight.status = "Completed"

    state.metrics.completed += 1
    state.metrics.max_delay = max(state.metrics.max_delay, flight.delay_minutes)

    plane.next_flight_index += 1

    if plane.next_flight_index >= len(plane.assigned_flights):
        return

    next_flight = plane.assigned_flights[plane.next_flight_index]
    
    delay = max(0, plane.available_time - next_flight.actual_departure)

    next_flight.actual_departure += delay
    next_flight.actual_arrival += delay

    if delay > 0:
        next_flight.propagated_delay += delay
        state.metrics.add_delay("propagated", delay)

   
    current_day = next_flight.actual_departure // state.config.day_minutes
    current_day_end = current_day * state.config.day_minutes + state.config.operating_day_end

    if next_flight.actual_departure > current_day_end:
        
        next_flight.actual_departure = get_next_day_start(next_flight.actual_departure, state.config)
        next_flight.actual_arrival = next_flight.actual_departure + next_flight.flight_time
        
        overnight_delay = next_flight.actual_departure - next_flight.scheduled_departure 
        next_flight.overnight_delay = overnight_delay
        state.metrics.add_delay("overnight", overnight_delay)
        
        
    heapq.heappush(state.events, Event(next_flight.actual_departure, "Departure", next_flight))


