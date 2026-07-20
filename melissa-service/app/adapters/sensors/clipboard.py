import ctypes
import ctypes.wintypes
from typing import Dict, Any
from app.ports.sensor import ContextSensor

class ClipboardSensor(ContextSensor):
    def __init__(self, enabled: bool = False):
        # Clipboard sensor is off by default for privacy
        self.enabled = enabled
        
    @property
    def name(self) -> str:
        return "clipboard"
        
    def get_current_state(self) -> Dict[str, Any]:
        """Returns the current text in the clipboard, if enabled."""
        if not self.enabled:
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
