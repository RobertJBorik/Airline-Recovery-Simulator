import heapq
import random

from classes import Event


def process_event(event, fleet, events, config, metrics):

    if event.event_type == "Departure":
        process_departure(event, fleet, events, config, metrics)

    elif event.event_type == "Arrival":
        process_arrival(event, fleet, events, config, metrics)


def process_departure(event, fleet, events, config, metrics):

    flight = event.flight

    # Weather delay
    if random.random() < config.weather_delay_probability:

        delay = random.randint(config.weather_delay_min, config.weather_delay_max)

        flight.actual_departure += delay
        flight.actual_arrival += delay

        flight.delay_minutes += delay
        flight.weather_delay += delay

        metrics.add_delay("weather", delay)


    # Gate delay
    if random.random() < config.gate_delay_probability:

        delay = random.randint(config.gate_delay_min, config.gate_delay_max)

        flight.actual_departure += delay
        flight.actual_arrival += delay

        flight.delay_minutes += delay
        flight.gate_delay += delay

        metrics.add_delay("gate", delay)
        
    # Maintenance delay
    if random.random() < config.maintenance_probability:

        delay = random.randint(config.maintenance_delay_min, config.maintenance_delay_max)

        flight.actual_departure += delay
        flight.actual_arrival += delay

        flight.delay_minutes += delay
        flight.maintenance_delay += delay

        metrics.add_delay("maintenance", delay)


    flight.status = "Departed"

    heapq.heappush(events, Event(time=flight.actual_arrival, event_type="Arrival", flight=flight))


def process_arrival(event, fleet, events, config, metrics):

    flight = event.flight
    plane = fleet[flight.aircraft_id]


    # Update aircraft state
    plane.current_airport = flight.destination

    plane.available_time = (flight.actual_arrival + config.turn_time)

    flight.status = "Arrived"

    metrics.completed += 1

    metrics.max_delay = max(metrics.max_delay, flight.delay_minutes)

    # Remove completed flight
    plane.remaining_flights.popleft()

    # No more flights for aircraft
    if not plane.remaining_flights:
        return

    next_flight = plane.remaining_flights[0]

    
    propagation_delay = max(0, plane.available_time - next_flight.scheduled_departure)
    next_flight.delay_minutes += propagation_delay

    next_flight.actual_departure = next_flight.scheduled_departure + propagation_delay

    next_flight.actual_arrival = next_flight.scheduled_arrival + propagation_delay


    if propagation_delay > 0:

        next_flight.propagated_delay += propagation_delay

        metrics.add_delay("propagated", propagation_delay)


    # Previous Flight Canceled
    if next_flight.actual_departure > config.operating_day_end:

        cancel_remaining_flights(plane, metrics, plane.available_time, reason="Exceeded operating window")

        return

    heapq.heappush(events, Event(time=next_flight.actual_departure, event_type="Departure", flight=next_flight))


def cancel_remaining_flights(plane, metrics, current_time, reason):

    while plane.remaining_flights:

        flight = plane.remaining_flights.popleft()

        propagated_delay = max(0, current_time - flight.scheduled_departure)

        flight.delay_minutes = propagated_delay
        flight.actual_departure = flight.scheduled_departure + propagated_delay
        flight.actual_arrival = flight.scheduled_arrival + propagated_delay
        flight.cancel(reason)

        if propagated_delay > 0:

            flight.propagated_delay = propagated_delay

            metrics.add_delay("propagated", propagated_delay)

        metrics.cancelled += 1