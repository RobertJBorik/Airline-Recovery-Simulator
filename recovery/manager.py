


class RecoveryManager:
    
    STRATEGIES = {
        "none": NoRecovery,
        "aircraftSwap": AircraftSwap
        "activateReserve": ActivateReserve
    }
    
    def __init__(self, strategy: str):
        
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown recovery strategy: {strategy}")
            
        self.policy = self.STRATEGIES[strategy]()
        
        
    def recover(self, event, delay, state):
        
        return self.policy.recover(event, delay, state)
    
class NoRecovery:

    def recover(self, event, delay, state):
        return False
    
class AircraftSwap:
    
    def recover(self, event, delay, state):
        return True
    
class ActivateReserve:
    
    def recover(self, event, delay, state):
        return True
