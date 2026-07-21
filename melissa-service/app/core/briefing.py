from typing import Dict, Any, List
from app.core.db import SessionLocal
from app.models import Goal
from sqlalchemy import select
from app.memory.store_semantic import global_semantic_store

async def pull_briefing_data() -> Dict[str, Any]:
    """
    Pulls data for the daily briefing:
    - Active goals from SQL
    - Unfinished items from semantic memory
    - Stated priorities from semantic memory
    """
    briefing_data = {}
    
    # 1. Pull active goals
    async with SessionLocal() as session:
        result = await session.execute(select(Goal).where(Goal.status == "active"))
        goals = result.scalars().all()
        briefing_data["active_goals"] = [
            {"id": g.id, "description": g.description} 
            for g in goals
        ]
        
    # 2. Pull unfinished items / priorities from semantic memory
    # We query chroma for concepts related to tasks and priorities
    unfinished_items = global_semantic_store.query_memory(
        query="yesterday unfinished tasks items",
        n_results=3
    )
    briefing_data["unfinished_items"] = unfinished_items
    
    priorities = global_semantic_store.query_memory(
        query="priorities main focus for today",
        n_results=3
    )
    briefing_data["priorities"] = priorities
    
    return briefing_data
