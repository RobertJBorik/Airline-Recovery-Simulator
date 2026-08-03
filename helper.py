def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02}:{mins:02}"

def format_day_time(minutes, config):

    day = (minutes // config.day_minutes) + 1

    day_minutes = minutes % config.day_minutes

    hour = day_minutes // 60
    minute = day_minutes % 60

    return f"Day {day} {hour:02d}:{minute:02d}"

def print_schedule(schedule, fleet, config):

    print("\nAircraft Status")
    print("-" * 40)

    for plane in fleet.values():
        print(
            f"{plane.tail_number} | "
            f"Base: {plane.base} | "
            f"Current: {plane.current_airport} | "
            f"Available: {format_day_time(plane.available_time, config)}"
        )


    print("\nScheduled Flights")
    print("-" * 100)
    print(f"{'Flight':<8} {'Aircraft':<10} {'Route':<15} {'Departure':<18} {'Arrival':<18} {'Time':<8}")
    print("-" * 100)

    for flight in schedule:

        route = f"{flight.origin} → {flight.destination}"

        print(
            f"{flight.flight_id:<8} "
            f"{flight.aircraft_id:<10} "
            f"{route:<15} "
            f"{flight.scheduled_departure:<5} "
            f"{format_day_time(flight.scheduled_departure, config):<18} "
            f"{format_day_time(flight.scheduled_arrival, config):<18} "
            f"{flight.flight_time:<8}"
        )

    print("-" * 100)
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
            "simulation_num": simulation,
            "flight_id": flight.flight_id,
            "aircraft": flight.aircraft_id,
            "simulation_day": flight.simulation_day,
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
            "overnight_delay": flight.overnight_delay,
            "propagated_delay": flight.propagated_delay,
            "status": flight.status,
            "reason": flight.cancellation_reason,
            
        })

    return rows

def get_day_start(day, config):
    return ((day - 1) * config.day_minutes) + config.operating_day_start


def get_day_end(day, config):
    return ((day - 1) * config.day_minutes) + config.operating_day_end


def get_next_day_start(current_time, config):

    current_day = current_time // config.day_minutes

    return ((current_day + 1) * config.day_minutes + config.operating_day_start)