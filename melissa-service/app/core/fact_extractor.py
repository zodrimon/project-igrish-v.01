import json
import logging
from typing import List, Dict, Any
from app.core.llm_registry import get_llm_provider
from app.core.db import SessionLocal
from app.models import Goal, Preference, Project, Habit

logger = logging.getLogger(__name__)

async def extract_facts(user_turn: str):
    """
    Analyzes the user's turn to extract structured facts like goals, preferences, etc.
    Writes them to the structured store.
    """
    llm_provider = get_llm_provider()
    
    prompt = f"""You are a fact extraction agent. Analyze the following user utterance and extract any structured facts.
Possible fact types: 'goal', 'preference', 'project', 'habit'.
Return ONLY a valid JSON array of objects, with each object having 'type' and 'content' keys.
If there are no clear facts to extract, return an empty array [].

User utterance: "{user_turn}"
"""
    
    messages = [{"role": "user", "content": prompt}]
    
    response_chunks = []
    try:
        async for chunk in llm_provider.generate(messages, stream=False):
            response_chunks.append(chunk)
            
        json_str = "".join(response_chunks).strip()
        
        # Remove markdown code blocks if present
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
            
        json_str = json_str.strip()
        
        if not json_str:
            return
            
        facts = json.loads(json_str)
        
        if facts and isinstance(facts, list):
            async with SessionLocal() as db:
                for fact in facts:
                    fact_type = fact.get("type")
                    content = fact.get("content")
                    
                    if not content:
                        continue
                        
                    if fact_type == "goal":
                        db.add(Goal(description=content))
                    elif fact_type == "preference":
                        # Simplistic key extraction for preference
                        key = content.lower().replace(" ", "_")[:20]
                        db.add(Preference(key=key, value=content))
                    elif fact_type == "project":
                        db.add(Project(name=content))
                    elif fact_type == "habit":
                        db.add(Habit(name=content))
                        
                await db.commit()
                logger.info(f"Extracted and saved {len(facts)} facts from turn.")
                
    except Exception as e:
        logger.error(f"Error extracting facts: {e}")
