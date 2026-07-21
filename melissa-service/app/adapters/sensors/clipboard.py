import ctypes
import ctypes.wintypes
from typing import Dict, Any
from app.ports.sensor import ContextSensor

class ClipboardSensor(ContextSensor):
    def __init__(self):
        # Clipboard sensor is off by default for privacy
        pass
        
    @property
    def name(self) -> str:
        return "clipboard"
        
    def get_current_state(self, preferences: Dict[str, str] = None) -> Dict[str, Any]:
        """Returns the current text in the clipboard, if enabled."""
        prefs = preferences or {}
        enabled = prefs.get("sensor.clipboard.enabled", "false").lower() == "true"
        if not enabled:
            return {"enabled": False, "content": None}
            
        try:
            import pyperclip
            text = pyperclip.paste()
            return {
                "enabled": True,
                "content": text if text else None
            }
        except Exception as e:
            return {"enabled": True, "content": None, "error": str(e)}
