from abc import ABC, abstractmethod
from typing import Any, Dict

class ContextSensor(ABC):
    """
    Interface for sensors that poll or stream data about the user's environment.
    (e.g., active window, visible screen text, etc.)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the sensor (e.g., 'active_window')"""
        pass
        
    @abstractmethod
    def get_current_state(self, preferences: Dict[str, str] = None) -> Dict[str, Any]:
        """Returns the current state dictionary for this sensor."""
        pass
