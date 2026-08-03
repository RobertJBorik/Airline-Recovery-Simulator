import heapq
import random

from classes import Event
from helper import get_next_day_start, get_day_end

def process_event(event, fleet, events, config, metrics):

    if event.event_type == "Departure":
        process_departure(event, fleet, events, config, metrics)

    elif event.event_type == "Arrival":
        process_arrival(event, fleet, events, config, metrics)


def process_departure(event, fleet, events, config, metrics):

    flight = event.flight
    total_delay = 0

    # Weather delay
    if random.random() < config.weather_delay_probability:
        delay = random.randint(config.weather_delay_min, config.weather_delay_max)

        flight.weather_delay += delay
        total_delay += delay
        metrics.add_delay("weather", delay)

    # Gate delay
    if random.random() < config.gate_delay_probability:
        delay = random.randint(config.gate_delay_min, config.gate_delay_max)

        flight.gate_delay += delay
        total_delay += delay
        metrics.add_delay("gate", delay)

    # Maintenance delay
    if random.random() < config.maintenance_probability:
        delay = random.randint(config.maintenance_delay_min, config.maintenance_delay_max)

        flight.maintenance_delay += delay
        total_delay += delay
        metrics.add_delay("maintenance", delay)

    # Update actual times
    flight.actual_departure += total_delay
    flight.actual_arrival += total_delay

    flight.status = "Departed"

    heapq.heappush(events, Event(time=flight.actual_arrival, event_type="Arrival", flight=flight))

def process_arrival(event, fleet, events, config, metrics):

    flight = event.flight
    plane = fleet[flight.aircraft_id]

    plane.current_airport = flight.destination
    plane.available_time = flight.actual_arrival + config.turn_time

    flight.status = "Completed"

    metrics.completed += 1
    metrics.max_delay = max(metrics.max_delay, flight.delay_minutes)

    plane.next_flight_index += 1

    if plane.next_flight_index >= len(plane.assigned_flights):
        return

    next_flight = plane.assigned_flights[plane.next_flight_index]
    
    delay = max(0, plane.available_time - next_flight.actual_departure)

    next_flight.actual_departure += delay
    next_flight.actual_arrival += delay

    if delay > 0:
        next_flight.propagated_delay += delay
        metrics.add_delay("propagated", delay)

   
    current_day = next_flight.actual_departure // config.day_minutes
    current_day_end = current_day * config.day_minutes + config.operating_day_end

    if next_flight.actual_departure > current_day_end:
        
        next_flight.actual_departure = get_next_day_start(next_flight.actual_departure, config)
        next_flight.actual_arrival = next_flight.actual_departure + next_flight.flight_time
        
        overnight_delay = next_flight.actual_departure - next_flight.scheduled_departure 
        next_flight.overnight_delay = overnight_delay
        metrics.add_delay("overnight", overnight_delay)
        
        
    heapq.heappush(events, Event(next_flight.actual_departure, "Departure", next_flight))


