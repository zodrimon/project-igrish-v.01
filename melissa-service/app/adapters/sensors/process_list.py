import psutil
from typing import Dict, Any, List
from app.ports.sensor import ContextSensor

class ProcessListSensor(ContextSensor):
    @property
    def name(self) -> str:
        return "running_processes"
        
    def get_current_state(self, preferences: Dict[str, str] = None) -> Dict[str, Any]:
        """Returns a list of unique running process names."""
        prefs = preferences or {}
        enabled = prefs.get("sensor.running_processes.enabled", "false").lower() == "true"
        if not enabled:
            return {"enabled": False, "count": 0, "processes": []}
            
        try:
            # We collect unique names to save space
            process_names = set()
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name']
                    if name:
                        process_names.add(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            return {
                "enabled": True,
                "count": len(process_names),
                "processes": sorted(list(process_names))
            }
        except Exception as e:
            return {"enabled": True, "count": 0, "processes": [], "error": str(e)}
