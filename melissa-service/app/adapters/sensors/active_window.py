import ctypes
import ctypes.wintypes
import psutil
from typing import Dict, Any
from app.ports.sensor import ContextSensor

class ActiveWindowSensor(ContextSensor):
    @property
    def name(self) -> str:
        return "active_window"
        
    def get_current_state(self) -> Dict[str, Any]:
        """Returns the title and process name of the active window using Win32 API."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return {"title": None, "process": None}
                
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
                
            return {
                "title": title,
                "process": process_name
            }
        except Exception as e:
            return {"title": None, "process": None, "error": str(e)}
