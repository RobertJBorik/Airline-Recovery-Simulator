from collections import defaultdict
from classes import Flight
from helper import get_day_start, get_day_end, get_next_day_start
#Build Schedule
def generate_schedule(airports, fleet, routes, config):

    schedule = []
    flight_number = 1

    for day in range(1, config.simulation_days + 1):

        day_start = get_day_start(day, config)
        day_end = get_day_end(day, config)

        for plane in fleet.values():

            if day == 1:
                plane.reset(config)
                plane.available_time = day_start

            elif plane.available_time < day_start:
                plane.available_time = day_start

        current_round_robin = defaultdict(int)
        while True:

            made_assignment = False

            aircraft_queue = sorted(fleet.values(), key=lambda plane: plane.available_time)

            for plane in aircraft_queue:

                if plane.available_time >= day_end:
                    continue

                candidates = get_candidate_routes(plane.current_airport, routes)

                route = choose_best_route(plane, candidates, airports, fleet, routes, config, current_round_robin)

                if route is None:
                    continue

                flight_time = calculate_flight_time(airports[route.origin], airports[route.destination], config)

                if plane.available_time + flight_time > day_end:
                    continue

                flight = create_flight(plane, route, flight_number, flight_time, day)

                flight_number += 1

                update_aircraft(plane, flight, config)

                schedule.append(flight)
                route_pair = tuple(sorted([flight.origin, flight.destination]))
                current_round_robin[route_pair] += 1

                made_assignment = True

            if not made_assignment:
                current_round_robin = defaultdict(int)
                break

    return schedule

def get_candidate_routes(current_airport, routes):
    return [route for route in routes.values() if route.origin == current_airport]

def choose_best_route(plane, candidates, airports, fleet, routes, config, current_round_robin):
    if not candidates:
        return None

    best_route = None
    best_score = float("-inf")

    for route in candidates:

        flight_time = calculate_flight_time(airports[route.origin], airports[route.destination], config)

        score = score_route(plane, route, airports, fleet, routes, config, flight_time, current_round_robin)

        if score > best_score:
            best_score = score
            best_route = route

    return best_route

def calculate_flight_time(origin, destination, config):

    distance = origin.distance_to(destination)

    flight_minutes = (distance / config.cruise_speed) * 60

    return round(flight_minutes + config.taxi_buffer)

def score_route(plane, route, airports, fleet, routes, config, flight_time, current_round_robin):

    origin = airports[route.origin]
    destination = airports[route.destination]

    score = 0

    # Route Demand Bonus
    score += route.route_weight * config.ROUTE_WEIGHT_MULTIPLIER

    # Hub Airport Bonus
    score += config.HUB_BONUS.get(destination.hub_size, 0)

    # Return to Base Bonus
    if route.destination == plane.base:
        remaining_time = config.operating_day_end - plane.available_time
        urgency = 1 - (remaining_time / config.operating_day_length)

        score += config.BASE_RETURN_BONUS * urgency

    # Avoid stranded aircraft
    future_routes = [r for r in routes.values() if r.origin == destination.code]

    if len(future_routes) == 0:
        score -= config.ENROUTE_PENALTY

    # Avoid Full Airports
    aircraft_at_destination = sum(1 for aircraft in fleet.values() if aircraft.current_airport == destination.code)

    airport_capacity = config.AIRPORT_CAPACITY.get(destination.hub_size, 1)

    if aircraft_at_destination > airport_capacity:
        congestion_amount = aircraft_at_destination - airport_capacity

        score -= (congestion_amount * config.AIRPORT_CONGESTION_PENALTY)

    #Avoid repeat route
    recent_routes = [(flight.origin, flight.destination) for flight in plane.assigned_flights[-4:]]

    if (route.origin, route.destination) in recent_routes:
        score -= config.RECENT_ROUTE_PENALTY

    
    # Route Coverage Balance
    
    route_pair = tuple(sorted([route.origin, route.destination]))

    scheduled_count = current_round_robin.get(route_pair, 0)

    score += config.ROUTE_COVERAGE_BONUS - scheduled_count * config.ROUTE_COVERAGE_PENALTY

    # Tiny Avoid Long FLight Penalty
    score -= (flight_time * config.FLIGHT_TIME_PENALTY)

    return score

def create_flight(plane, route, flight_number, flight_time, day):

    departure = plane.available_time
    arrival = departure + flight_time

    return Flight(
        flight_id=f"DL{flight_number:04}",
        aircraft_id=plane.tail_number,
        origin=route.origin,
        destination=route.destination,
        simulation_day=day,
        scheduled_departure=departure,
        scheduled_arrival=arrival,
    )

def update_aircraft(plane, flight, config):
    plane.current_airport = flight.destination
    plane.available_time = flight.scheduled_arrival + config.turn_time

    plane.assigned_flights.append(flight)

    plane.total_flights += 1
    plane.total_flight_minutes += flight.flight_time
    
