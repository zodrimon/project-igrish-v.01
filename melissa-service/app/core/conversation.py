from typing import List, Dict, Any

class ConversationBuffer:
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        # Each "turn" consists of a user message and an assistant message.
        self.history: List[Dict[str, Any]] = []
        
    def add_turn(self, user_message: str, assistant_message: str):
        """
        Adds a complete turn to the history. If history exceeds max_turns,
        removes the oldest turn (which is the oldest 2 messages: user + assistant).
        """
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_message})
        
        # Enforce max turns (each turn is 2 messages)
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]
            
    def get_history(self) -> List[Dict[str, Any]]:
        return self.history.copy()
        
    def clear(self):
        self.history = []

# Global buffer for the single active conversation
global_conversation_buffer = ConversationBuffer()
