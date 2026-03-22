# agents/news_agent.py

import sys
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).parent))

from runner import run_agent

load_dotenv(Path(__file__).parent.parent / ".env")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


# ── tool function ─────────────────────────────────────────────────────
async def search_news(query: str, max_results: int = 5) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://newsapi.org/v2/everything",
            params={                          # ← same pattern as HN agent
                "q": query,
                "apiKey": NEWS_API_KEY,
                "pageSize": max_results,
                "language": "en",
                "sortBy": "relevance"
            }
        )

    data = response.json()

    results = []
    for article in data.get("articles", []):  # ← NewsAPI uses "articles" not "hits"
        results.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "thumbnail": article.get("urlToImage"),  # ← image for the card
            "source": article.get("source", {}).get("name"),
            "published_at": article.get("publishedAt")
        })

    return str(results)


# ── tool schema ───────────────────────────────────────────────────────
NEWS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "Search news articles matching a query. Returns title, description, url, thumbnail and source.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query e.g. 'climate change'"
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

NEWS_TOOLS_MAP = {
    "search_news": search_news
}


# ── the agent ─────────────────────────────────────────────────────────
async def run_news_agent(user_interest: str) -> str:
    return await run_agent(
        system_prompt="""You are the News agent. Your job is to find 
        relevant news articles based on the user's interest.
        Search for articles and return a structured list of the top results.
        Always return results as a JSON list with fields:
        title, description, url, thumbnail, source, published_at.""",
        user_message=f"Find news articles about: {user_interest}",
        tools=NEWS_TOOLS,
        tools_map=NEWS_TOOLS_MAP
    )


# ── test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    async def test():
        print("Running News agent...")
        result = await run_news_agent("climate change")
        print("\nResult:")
        print(result)

    asyncio.run(test())