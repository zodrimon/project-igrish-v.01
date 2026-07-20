from typing import List, Dict, Any

def get_system_prompt() -> str:
    """
    Returns the system prompt for the Melissa persona.
    """
    return (
        "You are Melissa, an AI assistant. "
        "Your tone must be calm, concise, and supportive. "
        "You must always address the user as 'Boss'. "
        "Never use overly verbose language or robotic phrases. "
        "Keep your answers short and conversational, as if spoken aloud."
    )

def build_prompt(
    user_input: str, 
    conversation_history: List[Dict[str, Any]] = None,
    relevant_memories: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Builds the messages array for the LLM provider, injecting the system prompt
    and optionally prepending conversation history.
    """
    system_prompt_content = get_system_prompt()
    if relevant_memories:
        system_prompt_content += "\nRelevant past memories/context:\n"
        for mem in relevant_memories:
            system_prompt_content += f"- {mem}\n"
            
    messages = [{"role": "system", "content": system_prompt_content}]
    if conversation_history:
        messages.extend(conversation_history)
        
    messages.append({"role": "user", "content": user_input})
    
    return messages
