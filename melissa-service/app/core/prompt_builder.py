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

def build_briefing_prompt(briefing_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Builds the messages array for a Daily Briefing.
    """
    system_prompt_content = get_system_prompt()
    
    user_input = "Please provide my daily briefing. Here is the context:\n\n"
    
    if briefing_data.get("active_goals"):
        user_input += "Active Goals:\n"
        for g in briefing_data["active_goals"]:
            user_input += f"- {g['description']}\n"
        user_input += "\n"
        
    if briefing_data.get("unfinished_items"):
        user_input += "Unfinished Items from Yesterday:\n"
        for i in briefing_data["unfinished_items"]:
            user_input += f"- {i}\n"
        user_input += "\n"
        
    if briefing_data.get("priorities"):
        user_input += "Stated Priorities:\n"
        for p in briefing_data["priorities"]:
            user_input += f"- {p}\n"
        user_input += "\n"
        
    user_input += (
        "Draft a short, natural-sounding morning greeting and briefing. "
        "Do not list them like a robot; weave them into a spoken-style briefing."
    )
    
    return [
        {"role": "system", "content": system_prompt_content},
        {"role": "user", "content": user_input}
    ]
