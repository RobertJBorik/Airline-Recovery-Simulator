import heapq


def _push_departure(state, flight):
    from classes import Event

    heapq.heappush(
        state.events,
        Event(
            time=flight.actual_departure,
            event_type="Departure",
            flight=flight,
        ),
    )


class NoRecovery:
    def recover(self, event, delay, state):
        return False


def _apply_rotation_cycle(state, aircraft_cycle, delay, action):
    rotations = {
        aircraft.tail_number: aircraft.assigned_flights[aircraft.next_flight_index:]
        for aircraft in aircraft_cycle
    }
    affected_flights = {
        id(flights[0])
        for flights in rotations.values()
    }
    state.events = [
        queued_event
        for queued_event in state.events
        if not (
            queued_event.event_type == "Departure"
            and id(queued_event.flight) in affected_flights
        )
    ]
    heapq.heapify(state.events)

    for index, aircraft in enumerate(aircraft_cycle):
        incoming_aircraft = aircraft_cycle[(index + 1) % len(aircraft_cycle)]
        incoming_flights = rotations[incoming_aircraft.tail_number]
        aircraft.assigned_flights = incoming_flights
        aircraft.next_flight_index = 0

        for flight in incoming_flights:
            flight.aircraft_id = aircraft.tail_number
            flight.recovery_applied = True
            flight.recovery_action = action
            flight.recovery_aircraft_id = aircraft.tail_number

        _push_departure(state, incoming_flights[0])

    if action == "aircraft_swap":
        state.metrics.aircraft_swaps += 1
    else:
        state.metrics.cyclical_aircraft_swaps += 1
    state.metrics.recovered_delay_minutes += delay

class ActivateReserve:
    def __init__(self, reposition=False):
        self.reposition = reposition

    def recover(self, event, delay, state):
        source_plane = state.fleet[event.flight.aircraft_id]
        remaining_flights = source_plane.assigned_flights[source_plane.next_flight_index:]
        if not remaining_flights:
            return False

        next_flight = remaining_flights[0]
        candidates = []

        for plane in state.fleet.values():
            if not plane.reserve or plane.assigned_flights:
                continue

            reposition_minutes = 0
            if plane.current_airport != next_flight.origin:
                if not self.reposition:
                    continue

                if not state.airports:
                    raise ValueError(
                        "Airport data is required for the activateReserveReposition strategy"
                    )

                origin = state.airports.get(plane.current_airport)
                destination = state.airports.get(next_flight.origin)
                if origin is None or destination is None:
                    raise ValueError(
                        f"Missing airport data for reserve repositioning: "
                        f"{plane.current_airport} or {next_flight.origin}"
                    )

                reposition_minutes = round(
                    origin.distance_to(destination) / state.config.cruise_speed * 60
                ) + state.config.taxi_buffer

            ready_time = plane.available_time + reposition_minutes
            if reposition_minutes:
                ready_time += state.config.turn_time

            if ready_time <= next_flight.scheduled_departure:
                candidates.append((reposition_minutes, plane.tail_number, plane))

        if not candidates:
            return False

        reposition_minutes, _, reserve = min(candidates)
        reserve.current_airport = next_flight.origin
        reserve.available_time += reposition_minutes
        if reposition_minutes:
            reserve.available_time += state.config.turn_time
        reserve.assigned_flights = remaining_flights
        reserve.next_flight_index = 0
        source_plane.assigned_flights = source_plane.assigned_flights[:source_plane.next_flight_index]

        action = "reserve_reposition" if reposition_minutes else "reserve_activation"
        for index, flight in enumerate(remaining_flights):
            flight.aircraft_id = reserve.tail_number
            flight.recovery_applied = True
            flight.recovery_action = action
            flight.recovery_aircraft_id = reserve.tail_number
            flight.recovery_reposition_minutes = (
                reposition_minutes if index == 0 else 0
            )

        state.metrics.reserve_activations += 1
        state.metrics.recovered_delay_minutes += delay
        state.metrics.reserve_reposition_minutes += reposition_minutes
        if reposition_minutes:
            state.metrics.reserve_reposition_count += 1
        _push_departure(state, remaining_flights[0])
        return True


class SwapAircraft:
    def recover(self, event, delay, state):
        source_plane = state.fleet[event.flight.aircraft_id]
        source_flights = source_plane.assigned_flights[source_plane.next_flight_index:]
        if not source_flights:
            return False

        next_flight = source_flights[0]
        candidates = []

        for other_plane in state.fleet.values():
            if other_plane is source_plane:
                continue

            other_flights = other_plane.assigned_flights[other_plane.next_flight_index:]
            if not other_flights:
                continue

            other_next_flight = other_flights[0]
            if (
                other_plane.current_airport != next_flight.origin
                or other_next_flight.origin != next_flight.origin
                or other_next_flight.status != "Scheduled"
            ):
                continue

            if (
                other_plane.available_time > next_flight.scheduled_departure
                or source_plane.current_airport != other_next_flight.origin
                or source_plane.available_time > other_next_flight.actual_departure
            ):
                continue

            candidates.append((other_plane.tail_number, other_plane))

        if not candidates:
            return False

        _, other_plane = min(candidates, key=lambda candidate: candidate[0])
        _apply_rotation_cycle(
            state,
            [source_plane, other_plane],
            delay,
            "aircraft_swap",
        )
        return True


class CyclicalAircraftSwap:
    MAX_AIRCRAFT = 4

    def recover(self, event, delay, state):
        source_plane = state.fleet[event.flight.aircraft_id]
        source_flights = source_plane.assigned_flights[source_plane.next_flight_index:]
        if not source_flights:
            return False

        available_planes = [
            aircraft
            for aircraft in sorted(state.fleet.values(), key=lambda item: item.tail_number)
            if aircraft.assigned_flights[aircraft.next_flight_index:]
            and aircraft.assigned_flights[aircraft.next_flight_index].status == "Scheduled"
        ]
        if source_plane not in available_planes:
            return False

        def can_take_rotation(aircraft, rotation_owner):
            first_flight = rotation_owner.assigned_flights[
                rotation_owner.next_flight_index
            ]
            return (
                aircraft.current_airport == first_flight.origin
                and aircraft.available_time <= first_flight.actual_departure
            )

        def search(path, target_length):
            current = path[-1]
            for candidate in available_planes:
                if not can_take_rotation(current, candidate):
                    continue

                if candidate is source_plane:
                    if len(path) == target_length:
                        return path
                    continue

                if candidate in path or len(path) >= target_length:
                    continue
                cycle = search(path + [candidate], target_length)
                if cycle:
                    return cycle
            return None

        cycle = None
        for cycle_length in range(3, self.MAX_AIRCRAFT + 1):
            cycle = search([source_plane], cycle_length)
            if cycle:
                break

        if not cycle:
            return False

        _apply_rotation_cycle(
            state,
            cycle,
            delay,
            "cyclical_aircraft_swap",
        )
        return True


class RecoveryManager:
    STRATEGIES = {
        "none": NoRecovery,
        "activateReserve": ActivateReserve,
        "activateReserveReposition": lambda: ActivateReserve(reposition=True),
        "aircraftSwap": SwapAircraft,
        "cyclicalAircraftSwap": CyclicalAircraftSwap,
    }

    def __init__(self, strategy: str):
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown recovery strategy: {strategy}")

        self.policy = self.STRATEGIES[strategy]()

    def recover(self, event, delay, state):
        return self.policy.recover(event, delay, state)
