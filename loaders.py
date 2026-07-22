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
            flight_time=route["flight_time"],
            flights_per_day=route["flights_per_day"],
        )
        
        routes[(forward.origin, forward.destination)] = forward
        
        if route.get("bidirectional", False):
            reverse = Route(
                origin=route["destination"],
                destination=route["origin"],
                flight_time=route["flight_time"],
                flights_per_day=route["flights_per_day"],
            )

            routes[(reverse.origin, reverse.destination)] = reverse
    return routes


def load_airports(filename):
    airports = {}

    with open(filename, "r") as f:
        json_data = json.load(f)
        
    for airport in json_data:
        location = Airport(
            code=airport["code"],
            name=airport["name"]
        )
        
        airports[location.code] = location
    
    return airports

def load_aircraft(filename):
    aircrafts = {}
    
    with open(filename, "r") as f:
        json_data = json.load(f)
        
    for aircraft in json_data:
        plane = Aircraft(
            tail_number=aircraft["tail_number"],
            base=aircraft["base"],
            reserve=aircraft.get("reserve", False)
        )
        
        aircrafts[plane.tail_number] = plane

    return aircrafts
