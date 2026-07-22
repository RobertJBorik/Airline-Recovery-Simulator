def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02}:{mins:02}"

def print_schedule(schedule, aircraft, routes):

    print("\nRemaining Flights")
    print("-" * 40)
    for route in routes.values():
        if route.remaining_flights > 0:
            print(f"{route.origin} -> {route.destination}: {route.remaining_flights}")
            
    for plane in aircraft.values():
        print(plane.tail_number, "base:", plane.base, "current:", plane.current_airport, "time:", plane.available_time)
    
    print("\nScheduled Flights")
    print("-" * 40)  
    print("=" * 80)
    print(f"{'Flight':<8} {'Aircraft':<8} {'Route':<15} {'Departure':<10} {'Arrival':<10}")
    print("=" * 80)

    for flight in schedule:
        route = f"{flight.origin} → {flight.destination}"

        print(
            f"{flight.flight_id:<8} "
            f"{flight.aircraft_id:<8} "
            f"{route:<15} "
            f"{format_time(flight.scheduled_departure):<10} "
            f"{format_time(flight.scheduled_arrival):<10}"
        )

    print("=" * 80)
    print(f"Total Flights Scheduled: {len(schedule)}")
    

def reset_fleet(fleet):

    for plane in fleet.values():
        plane.current_airport = plane.base
        plane.available_time = 360
        plane.remaining_flights = deque(plane.assigned_flights)
        
def collect_flight_results(schedule, simulation):
    rows = []

    for flight in schedule:
        rows.append({
            "simulation": simulation,
            "flight_id": flight.flight_id,
            "aircraft": flight.aircraft_id,
            "origin": flight.origin,
            "destination": flight.destination,
            "scheduled_departure": flight.scheduled_departure,
            "actual_departure": flight.actual_departure,
            "scheduled_arrival": flight.scheduled_arrival,
            "actual_arrival": flight.actual_arrival,
            "delay_minutes": flight.delay_minutes,
            "weather_delay": flight.weather_delay,
            "gate_delay": flight.gate_delay,
            "maintenance_delay": flight.maintenance_delay,
            "propagated_delay": flight.propagated_delay,
            "status": flight.status,
            "reason": flight.cancellation_reason,
        })

    return rows