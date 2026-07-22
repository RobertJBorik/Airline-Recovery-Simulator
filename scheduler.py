from classes import Flight

#Build Schedule
def generate_schedule(fleet, routes, config):
    # Reset aircraft state
    for plane in fleet.values():
        plane.reset(config)

    # Reset route demand
    for route in routes.values():
        route.reset()
        
    schedule = []
    flight_number = 1
    for plane in fleet.values():

        while plane.available_time < config.operating_day_end:

            candidates = get_candidate_routes(plane.current_airport, routes)

            route = choose_best_route(candidates)

            if route is None or (plane.available_time + route.flight_time) > config.operating_day_end:
                break
            
            flight = create_flight(plane, route, flight_number)
            flight_number += 1
            
            update_aircraft(plane, route, flight, config)

            schedule.append(flight)
            
    return schedule


def get_candidate_routes(current_airport, routes):
    candidates = []

    for route in routes.values():
        if (route.origin == current_airport and route.remaining_flights > 0):
            candidates.append(route)

    return candidates

def choose_best_route(candidates):
    if not candidates:
        return None
    
    #Sort by Most Remaining flights > Shortest Flight Time > Alphabetical Destination
    best = sorted(candidates, key=lambda r: (-r.remaining_flights, r.flight_time, r.destination))
    # TODO: Eventually add a demand or something as a sorting method
    return best[0]

def create_flight(plane, route, flight_number):

    departure_time = plane.available_time
    arrival_time = departure_time + route.flight_time
    #TODO: eventually add an assertion to ensure this is all good
    return Flight(
        flight_id=f"DL{flight_number:04}",
        aircraft_id=plane.tail_number,

        origin=route.origin,
        destination=route.destination,

        scheduled_departure=departure_time,
        scheduled_arrival=arrival_time,
    )

def update_aircraft(plane, route, flight, config):
    plane.current_airport = flight.destination
    plane.available_time = (flight.scheduled_arrival + config.turn_time)
    plane.assigned_flights.append(flight)
    route.remaining_flights -= 1

    
