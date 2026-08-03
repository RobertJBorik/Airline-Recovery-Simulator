import json
import heapq

from classes import Airport, Aircraft, Route

def load_routes(filename):
    routes = {}

    with open(filename, "r") as f:
        json_data = json.load(f)

    for route in json_data:
        forward = Route(
            origin=route["origin"],
            destination=route["destination"],
            route_weight=route.get("route_weight", 1),
            bidirectional=route.get("bidirectional", True),
        )
        
        routes[forward.key] = forward
        
        if forward.bidirectional:
            reverse = Route(
                origin=forward.destination,
                destination=forward.origin,
                route_weight=forward.route_weight,
                bidirectional=True,
            )

            routes[reverse.key] = reverse
    return routes


def load_airports(filename):
    airports = {}

    with open(filename, "r") as f:
        json_data = json.load(f)
        
    for airport in json_data:
        location = Airport(
            code=airport["code"],
            name=airport["name"],
            city=airport["city"],
            state=airport["state"],
            hub_size=airport["hub_size"],
            latitude=airport["latitude"],
            longitude=airport["longitude"],
        )
        
        if location.code in airports:
            raise ValueError(f"Duplicate airport code: {location.code}")
        airports[location.code] = location
    
    return airports

def load_aircraft(filename):
    aircraft = {}
    
    with open(filename, "r") as f:
        json_data = json.load(f)
        
    for aircraft_data in json_data:
        plane = Aircraft(
            tail_number=aircraft_data["tail_number"],
            base=aircraft_data["base"],
            reserve=aircraft_data.get("reserve", False)
        )
        
        if plane.tail_number in aircraft:
            raise ValueError(f"Duplicate aircraft Num: {plane.tail_number}")

        aircraft[plane.tail_number] = plane

    return aircraft
