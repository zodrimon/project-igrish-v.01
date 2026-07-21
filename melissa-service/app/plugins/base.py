from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class PluginBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin."""
        pass
        
    async def get_context_facts(self) -> Dict[str, Any]:
        """
        Return a dictionary of context facts to inject into the system prompt.
        This can be asynchronous to allow querying external APIs or reading files.
        """
        return {}
        
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Return a list of LLM tool definitions (e.g. OpenAI function calling schema).
        """
        return []
        
    async def evaluate_proactive_triggers(self) -> Optional[Dict[str, Any]]:
        """
        Evaluate if a proactive trigger should fire.
        Returns a dictionary describing the nudge (e.g., {"nudge_type": "coding_suggestion", "content": "..."}) if it should fire, else None.
        """
        return None
