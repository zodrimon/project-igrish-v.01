import psutil
from typing import Dict, Any
from app.ports.sensor import ContextSensor

class SystemStateSensor(ContextSensor):
    @property
    def name(self) -> str:
        return "system_state"
        
    def get_current_state(self) -> Dict[str, Any]:
        """Returns CPU and memory usage statistics."""
        try:
            # We use interval=None to get immediate reading since last call
            cpu_percent = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": mem.percent
            }
        except Exception as e:
            return {"cpu_percent": 0.0, "memory_percent": 0.0, "error": str(e)}
