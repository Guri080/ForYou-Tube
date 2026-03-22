# agents/hn_agent.py

import sys
import httpx
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from runner import run_agent

# ── tool function ─────────────────────────────────────────────────────
async def search_hn(query: str, max_results: int = 5) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://hn.algolia.com/api/v1/search",
            params={
                "query": query,
                "tags": "story",        # only return stories, not comments
                "hitsPerPage": max_results
            }
        )
        data = response.json()

    results = []
    for hit in data.get("hits", []):
        results.append({
            "title": hit.get("title"),
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}",
            "hn_url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
            "points": hit.get("points", 0),
            "num_comments": hit.get("num_comments", 0),
            "author": hit.get("author"),
        })

    return str(results)


# ── tool schema ───────────────────────────────────────────────────────
HN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_hn",
            "description": "Search Hacker News for stories matching a query. Returns title, url, points, and comment count.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query e.g. 'machine learning'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return, max 10",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
]

HN_TOOLS_MAP = {
    "search_hn": search_hn
}


# ── the agent ─────────────────────────────────────────────────────────
async def run_hn_agent(user_interest: str) -> str:
    return await run_agent(
        system_prompt="""You are the Hacker News agent. Your job is to find 
        relevant Hacker News stories based on the user's interest.
        Search for stories and return a structured list of the top results.
        Always return results as a JSON list with fields:
        title, url, hn_url, points, num_comments, author.""",
        user_message=f"Find Hacker News stories about: {user_interest}",
        tools=HN_TOOLS,
        tools_map=HN_TOOLS_MAP
    )


# ── test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    async def test():
        print("Running HN agent...")
        result = await run_hn_agent("machine learning")
        print("\nResult:")
        print(result)

    asyncio.run(test())