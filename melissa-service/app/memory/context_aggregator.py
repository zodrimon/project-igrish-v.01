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
    
    # 2. Combine all context
    all_context = structured_memories + semantic_memories
    
    # 3. Get recent conversation history
    history = global_conversation_buffer.get_history()
    
    # 4. Build prompt
    return build_prompt(user_text, conversation_history=history, relevant_memories=all_context)
