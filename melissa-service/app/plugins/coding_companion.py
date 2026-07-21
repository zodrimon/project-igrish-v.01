from typing import Dict, Any, Optional
from app.plugins.base import PluginBase
from app.core.context_snapshot import global_context_snapshot

class CodingCompanionPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "CodingCompanion"
        
    async def get_context_facts(self) -> Dict[str, Any]:
        """
        Check the active window. If it's VS Code, extract the project name.
        """
        facts = {}
        snapshot = global_context_snapshot.get_state()
        active_window_data = snapshot.get("active_window", {})
        
        # Example window title: "main.py - project-igrish-v.01 - Visual Studio Code"
        # Or: "project-igrish-v.01 - Visual Studio Code"
        title = active_window_data.get("title", "")
        if title and "Visual Studio Code" in title:
            # Simple heuristic to extract the project name
            parts = title.split("-")
            if len(parts) >= 2:
                # The project name is typically the second to last part (before "Visual Studio Code")
                # But it could also be the first part if no file is open.
                # Let's grab the part right before "Visual Studio Code"
                for i, part in enumerate(parts):
                    if "Visual Studio Code" in part and i > 0:
                        project_name = parts[i-1].strip()
                        facts["active_project"] = project_name
                        facts["ide"] = "VS Code"
                        break
        return facts
