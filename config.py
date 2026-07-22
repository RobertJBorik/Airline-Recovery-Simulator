from dataclasses import dataclass 

@dataclass
class Config:
    # Operations
    operating_day_start: int = 360
    operating_day_end: int = 1320
    turn_time: int = 45

    # Delay probabilities
    weather_delay_probability: float = 0.05
    gate_delay_probability: float = 0.08
    maintenance_probability: float = 0.01

    # Delay ranges
    weather_delay_min: int = 15
    weather_delay_max: int = 60

    gate_delay_min: int = 5
    gate_delay_max: int = 25

    maintenance_delay_min: int = 30
    maintenance_delay_max: int = 120

    random_seed: int = 42