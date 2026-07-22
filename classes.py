from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque

@dataclass
class Airport:
    code: str
    name: str
    
@dataclass
class Aircraft:
    tail_number: str
    base: str
    reserve: bool = False

    current_airport: str = ""
    available_time: int = 0
    assigned_flights: list[Flight] = field(default_factory=list)
    remaining_flights: deque[Flight] = field(default_factory=deque)
    

    def __post_init__(self):
        self.current_airport = self.base
        self.available_time = 0
        
    def reset(self, config):
        self.current_airport = self.base
        self.available_time = config.operating_day_start

        self.remaining_flights = deque(self.assigned_flights)

@dataclass
class Flight:
    flight_id: str

    aircraft_id: str | None

    origin: str
    destination: str

    scheduled_departure: int
    scheduled_arrival: int

    actual_departure: int = 0
    actual_arrival: int = 0

    delay_minutes: int = 0
    
    weather_delay: int = 0
    gate_delay: int = 0
    maintenance_delay: int = 0
    propagated_delay: int = 0
    cancellation_reason: str = "Not Cancelled"
    status: str = "Scheduled"

    def __post_init__(self):
        self.actual_departure = self.scheduled_departure
        self.actual_arrival = self.scheduled_arrival


    def reset(self):
        self.actual_departure = self.scheduled_departure
        self.actual_arrival = self.scheduled_arrival
        self.delay_minutes = 0
        self.weather_delay = 0
        self.gate_delay = 0
        self.maintenance_delay = 0
        self.propagated_delay = 0
        self.status = "Scheduled"
        self.cancellation_reason = "Not Cancelled"


    def cancel(self, reason):
        self.status = "Cancelled"
        self.cancellation_reason = reason
        
@dataclass
class Route:
    origin: str
    destination: str
    flight_time: int
    flights_per_day: int
    remaining_flights: int = 0
    
    def reset(self):
        self.remaining_flights = self.flights_per_day


    
@dataclass(order=True)
class Event:
    time: int
    event_type: str      # Departure / Arrival #TODO define enum to rpevent typos
    flight: Flight = field(compare=False)        