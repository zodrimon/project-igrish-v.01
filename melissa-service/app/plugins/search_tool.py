import asyncio
import logging

logger = logging.getLogger(__name__)

async def search_docs(query: str, max_results: int = 3) -> str:
    """
    Perform a scoped documentation search using DuckDuckGo.
    This restricts the search to well-known documentation sites.
    """
    try:
        from duckduckgo_search import DDGS
        
        # Scope the query to doc sites
        scoped_query = f"{query} site:docs.python.org OR site:developer.mozilla.org OR site:react.dev OR site:github.com OR site:stackoverflow.com"
        
        # DDGS is synchronous by default but supports async. We'll run it in a thread.
        def _do_search():
            with DDGS() as ddgs:
                results = list(ddgs.text(scoped_query, max_results=max_results))
                return results
                
        results = await asyncio.to_thread(_do_search)
        
        if not results:
            return "No documentation found for your query."
            
        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nURL: {r.get('href')}\n")
            
        return "\n".join(formatted_results)
    except Exception as e:
        logger.error(f"Doc search failed: {e}")
        return f"Documentation search failed: {e}"
