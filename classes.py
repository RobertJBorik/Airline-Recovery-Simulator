from __future__ import annotations
from math import radians, sin, cos, sqrt, atan2
from dataclasses import dataclass, field
from collections import deque

from recovery.manager import RecoveryManager


@dataclass
class Airport:
    code: str
    name: str
    city: str
    state: str
    hub_size: str
    latitude: float
    longitude: float

    def distance_to(self, other: "Airport") -> float:
        """Returns great-circle distance in miles."""
    
        R = 3958.8  # Earth radius in miles
    
        lat1 = radians(self.latitude)
        lon1 = radians(self.longitude)
        lat2 = radians(other.latitude)
        lon2 = radians(other.longitude)
    
        dlat = lat2 - lat1
        dlon = lon2 - lon1
    
        a = (
            sin(dlat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        )
    
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
        return R * c
    
@dataclass
class Aircraft:
    tail_number: str
    base: str
    reserve: bool = False

    # ---- Dynamic Sim Info -------
    current_airport: str = ""
    available_time: int = 0
    assigned_flights: list[Flight] = field(default_factory=list)
    next_flight_index: int = 0
    total_flights: int = 0
    total_flight_minutes: int = 0

    def __post_init__(self):
        self.current_airport = self.base

    def clear_schedule(self):
        self.assigned_flights.clear()
    
    def reset(self, config):
        self.current_airport = self.base
        self.available_time = config.operating_day_start
        self.total_flights = 0
        self.total_flight_minutes = 0
    
@dataclass
class Flight:
    flight_id: str
    aircraft_id: str | None
    origin: str
    destination: str
    scheduled_departure: int = 0
    scheduled_arrival: int = 0

    actual_departure: int = 0
    actual_arrival: int = 0
    simulation_day: int = 0
    weather_delay: int = 0
    gate_delay: int = 0
    maintenance_delay: int = 0
    propagated_delay: int = 0
    overnight_delay: int = 0

    cancellation_reason: str | None = None
    status: str = "Scheduled"

    def __post_init__(self):
        self.actual_departure = self.scheduled_departure
        self.actual_arrival = self.scheduled_arrival

    @property
    def delay_minutes(self) -> int:
        """Total delay accumulated from all sources."""
        return (self.weather_delay + self.gate_delay + self.maintenance_delay + self.propagated_delay + self.overnight_delay)

    @property
    def completed(self) -> bool:
        return self.status == "Completed"

    @property
    def cancelled(self) -> bool:
        return self.status == "Cancelled"
    
    @property
    def actual_flight_time(self):
        return self.actual_arrival - self.actual_departure

    @property
    def flight_time(self) -> int:
        return self.scheduled_arrival - self.scheduled_departure

    def reset(self):
        self.actual_departure = self.scheduled_departure
        self.actual_arrival = self.scheduled_arrival

        self.weather_delay = 0
        self.gate_delay = 0
        self.maintenance_delay = 0
        self.propagated_delay = 0

        self.status = "Scheduled"
        self.cancellation_reason = None

    def cancel(self, reason: str):
        self.status = "Cancelled"
        self.cancellation_reason = reason
        self.aircraft_id = None
    
@dataclass(frozen=True)
class Route:
    origin: str
    destination: str
    route_weight: int = 1
    bidirectional: bool = True
    
    @property
    def key(self):
        return (self.origin, self.destination)
    
@dataclass(order=True)
class Event:
    time: int
    event_type: str      # Departure / Arrival #TODO define enum to rpevent typos
    flight: Flight = field(compare=False)        
    
@dataclass
class SimulationState:
    flights: dict[str, Flight]
    fleet: dict[str, Aircraft]
    events: list[Event]
    metrics: SimulationMetrics
    config: Config
    recovery_manager: object #RecoveryManager future proofing circular import