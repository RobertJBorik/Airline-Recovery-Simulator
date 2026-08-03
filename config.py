from dataclasses import dataclass 

@dataclass
class Config:
    # Simulation
    simulation_days: int = 7
    day_minutes: int = 1440

    # Daily Operations
    operating_day_start: int = 360       # 06:00
    operating_day_end: int = 1320        # 22:00

    # Aircraft Operations
    turn_time: int = 45                  # minutes between flights

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
    
    #Scheduler Weights
    cruise_speed = 400 #mph
    taxi_buffer = 15 #mins
    ROUTE_WEIGHT_MULTIPLIER = 5
    HUB_BONUS = {"major": 40, "medium": 20, "small": 5,}
    AIRPORT_CAPACITY = {"major": 12, "medium": 8,"small": 5,}
    BASE_RETURN_BONUS = 30
    ENROUTE_PENALTY = 50
    AIRPORT_CONGESTION_PENALTY = 5
    RECENT_ROUTE_PENALTY = 50
    FLIGHT_TIME_PENALTY = 0.1
    RETURN_HOME_WINDOW = 180
    ROUTE_COVERAGE_PENALTY = 20
    ROUTE_COVERAGE_BONUS = 40
    
    @property
    def operating_day_length(self):
        return self.operating_day_end - self.operating_day_start