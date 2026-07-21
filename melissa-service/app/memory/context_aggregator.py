import asyncio
from typing import List, Dict, Any
from sqlalchemy import select
from app.core.db import SessionLocal
from app.models import Goal, Project, Preference, Habit
from app.memory.store_semantic import global_semantic_store
from app.core.conversation import global_conversation_buffer
from app.core.prompt_builder import build_prompt

async def _get_structured_context() -> List[str]:
    context = []
    async with SessionLocal() as db:
        # Fetch goals
        goals_result = await db.execute(select(Goal).where(Goal.status == "active"))
        goals = [g.description for g in goals_result.scalars().all()]
        if goals:
            context.append(f"Active Goals: {', '.join(goals)}")
            
        # Fetch projects
        projects_result = await db.execute(select(Project).where(Project.status == "active"))
        projects = [p.name for p in projects_result.scalars().all()]
        if projects:
            context.append(f"Active Projects: {', '.join(projects)}")
            
        # Fetch preferences
        prefs_result = await db.execute(select(Preference))
        prefs = [f"{p.key}: {p.value}" for p in prefs_result.scalars().all()]
        if prefs:
            context.append(f"User Preferences: {', '.join(prefs)}")
            
        # Fetch habits
        habits_result = await db.execute(select(Habit))
        habits = [f"{h.name} ({h.frequency})" for h in habits_result.scalars().all()]
        if habits:
            context.append(f"Habits: {', '.join(habits)}")
            
    return context

async def build_augmented_prompt(user_text: str) -> List[Dict[str, Any]]:
    """
    Aggregates semantic memory, structured memory, and conversation history
    into a single messages payload for the LLM.
    """
    # 1. Fetch semantic memory
    def _query_semantic():
        return global_semantic_store.query_memory(user_text, n_results=3)
    
    semantic_memories, structured_memories = await asyncio.gather(
        asyncio.to_thread(_query_semantic),
        _get_structured_context()
    )
    
    # 3. Get recent conversation history
    history = global_conversation_buffer.get_history()
    
    # Combine into single context block
    context_text = "Structured Context:\n"
    if structured_memories:
        for item in structured_memories:
            context_text += f"- {item}\n"
    else:
        context_text += "None\n"
        
    context_text += "\nSemantic Context:\n"
    if semantic_memories:
        for mem in semantic_memories:
            context_text += f"- {mem}\n"
    else:
        context_text += "None\n"
        
    from app.core.context_snapshot import global_context_snapshot
    snapshot_state = global_context_snapshot.get_state()
    if snapshot_state:
        context_text += "\nReal-Time Context Snapshot:\n"
        for sensor_name, state in snapshot_state.items():
            context_text += f"[{sensor_name}]: {state}\n"
            
    from app.core.plugin_loader import global_plugin_registry
    plugins = global_plugin_registry.get_all_plugins()
    if plugins:
        plugin_facts = {}
        # get_context_facts is async
        fact_tasks = [p.get_context_facts() for p in plugins]
        results = await asyncio.gather(*fact_tasks, return_exceptions=True)
        
        for plugin, result in zip(plugins, results):
            if isinstance(result, Exception):
                pass
            elif result:
                plugin_facts[plugin.name] = result
                
        if plugin_facts:
            context_text += "\nPlugin Context Facts:\n"
            for p_name, p_facts in plugin_facts.items():
                context_text += f"[{p_name}]: {p_facts}\n"
    
    # Delegate to build_prompt
    return build_prompt(user_text, conversation_history=history, relevant_memories=[context_text])
