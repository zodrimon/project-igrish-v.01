import ctypes
import ctypes.wintypes
from typing import Dict, Any
from app.ports.sensor import ContextSensor

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("dwTime", ctypes.c_uint)
    ]

class InputActivitySensor(ContextSensor):
    @property
    def name(self) -> str:
        return "input_activity"
        
    def get_current_state(self) -> Dict[str, Any]:
        """Returns the idle time in seconds using Win32 API."""
        try:
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                idle_seconds = millis / 1000.0
                return {
                    "idle_seconds": round(idle_seconds, 1),
                    "is_active": idle_seconds < 60.0
                }
            return {"idle_seconds": 0, "is_active": True}
        except Exception as e:
            return {"idle_seconds": 0, "is_active": True, "error": str(e)}
