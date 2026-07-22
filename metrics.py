from dataclasses import dataclass, field

@dataclass
class SimulationMetrics:
    total_flights: int = 0
    completed: int = 0
    cancelled: int = 0

    total_delay_minutes: int = 0
    max_delay: int = 0

    weather_delay_minutes: int = 0
    gate_delay_minutes: int = 0
    maintenance_delay_minutes: int = 0
    propagated_delay_minutes: int = 0

    def add_delay(self, delay_type, minutes):
        self.total_delay_minutes += minutes

        if delay_type == "weather":
            self.weather_delay_minutes += minutes

        elif delay_type == "gate":
            self.gate_delay_minutes += minutes

        elif delay_type == "maintenance":
            self.maintenance_delay_minutes += minutes

        elif delay_type == "propagated":
            self.propagated_delay_minutes += minutes


    def summary(self):
        average_delay = (
            self.total_delay_minutes / self.total_flights
            if self.total_flights
            else 0
        )

        return {
            "total_flights": self.total_flights,
            "completed": self.completed,
            "cancelled": self.cancelled,
            "total_delay_minutes": self.total_delay_minutes,
            "average_delay": round(average_delay, 2),
            "max_delay": self.max_delay,

            "weather_delay": self.weather_delay_minutes,
            "gate_delay": self.gate_delay_minutes,
            "maintenance_delay": self.maintenance_delay_minutes,
            "propagated_delay": self.propagated_delay_minutes,
        }
    def reset(self):
        self.total_flights = 0
        self.completed = 0
        self.cancelled = 0
    
        self.total_delay_minutes = 0
        self.max_delay = 0
    
        self.weather_delay_minutes = 0
        self.gate_delay_minutes = 0
        self.maintenance_delay_minutes = 0
        self.propagated_delay_minutes = 0