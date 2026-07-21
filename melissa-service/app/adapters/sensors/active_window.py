import ctypes
import ctypes.wintypes
import psutil
from typing import Dict, Any
from app.ports.sensor import ContextSensor

class ActiveWindowSensor(ContextSensor):
    @property
    def name(self) -> str:
        return "active_window"
        
    def get_current_state(self, preferences: Dict[str, str] = None) -> Dict[str, Any]:
        """Returns the title and process name of the active window using Win32 API."""
        prefs = preferences or {}
        enabled = prefs.get("sensor.active_window.enabled", "true").lower() == "true"
        if not enabled:
            return {"enabled": False, "process_name": None, "window_title": None, "category": "unknown"}
            
        detailed = prefs.get("sensor.active_window.detailed", "false").lower() == "true"
        
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return {"window_title": None, "process_name": None, "category": "unknown"}
                
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            
            pid = ctypes.wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            try:
                process = psutil.Process(pid.value)
                process_name = process.name()
            except psutil.Error:
                process_name = None
                
            from app.core.classification import AppClassifier
            classifier = AppClassifier()
            category = classifier.classify(process_name, title)
                
            return {
                "enabled": True,
                "process_name": process_name if detailed else None,
                "window_title": title if detailed else None,
                "category": category
            }
        except Exception as e:
            return {"enabled": True, "process_name": None, "window_title": None, "category": "unknown", "error": str(e)}
