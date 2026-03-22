# backend/digest/tinyfish_scraper.py

import os
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")
TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")

# ── topic → scrape targets mapping ───────────────────────────────────
# For each topic category, we define which URLs to scrape
# Tinyfish handles the actual extraction with natural language goals

TOPIC_SOURCES = {
    "finance":          ["https://finance.yahoo.com", "https://markets.businessinsider.com"],
    "stocks":           ["https://finance.yahoo.com/trending-tickers", "https://markets.businessinsider.com"],
    "crypto":           ["https://coinmarketcap.com", "https://decrypt.co"],
    "machine learning": ["https://paperswithcode.com", "https://techcrunch.com/tag/machine-learning"],
    "ai":               ["https://techcrunch.com/tag/artificial-intelligence", "https://venturebeat.com/ai"],
    "nba":              ["https://espn.com/nba", "https://bleacherreport.com/nba"],
    "nfl":              ["https://espn.com/nfl", "https://bleacherreport.com/nfl"],
    "gaming":           ["https://ign.com", "https://www.gamespot.com"],
    "indie games":      ["https://itch.io/games/new-and-popular", "https://www.gamesindustry.biz"],
    "health":           ["https://www.healthline.com/health-news", "https://medicalxpress.com"],
    "science":          ["https://www.sciencedaily.com", "https://phys.org"],
    "climate":          ["https://www.carbonbrief.org", "https://insideclimatenews.org"],
    "politics":         ["https://politico.com", "https://thehill.com"],
    "startups":         ["https://techcrunch.com/startups", "https://news.ycombinator.com"],
    "default":          ["https://news.ycombinator.com", "https://techcrunch.com"],
}


def get_sources_for_topic(topic: str) -> list[str]:
    """Find the best matching sources for a topic."""
    topic_lower = topic.lower()
    for key in TOPIC_SOURCES:
        if key in topic_lower or topic_lower in key:
            return TOPIC_SOURCES[key]
    return TOPIC_SOURCES["default"]


async def scrape_url(url: str, topic: str) -> dict | None:
    """
    Scrape a single URL with Tinyfish.
    Returns extracted articles or None if failed.
    """
    goal = f"""Extract the 3 most recent and relevant articles or stories about "{topic}".
    For each article return exactly this JSON structure:
    [{{"title": str, "summary": str, "url": str, "source": str}}]
    Return ONLY the JSON array, nothing else."""

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST",
                "https://agent.tinyfish.ai/v1/automation/run-sse",
                headers={
                    "X-API-Key": TINYFISH_API_KEY,
                    "Content-Type": "application/json"
                },
                json={"url": url, "goal": goal}
            ) as response:

                # read the SSE stream looking for the COMPLETE event
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue

                    raw = line[5:].strip()
                    if not raw:
                        continue
                    
                    # ---debug line---
                    # print(f"[debug] raw event: {raw[:200]}")


                    try:
                        event = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    # this is the final event with our data
                    if event.get("type") == "COMPLETE" and event.get("status") == "COMPLETED":
                        result = event.get("result", {})
                        articles = result.get("result", [])
                        if articles:
                            return {
                                "url": url,
                                "articles": articles if isinstance(articles, list) else []
                            }

    except Exception as e:
        print(f"[tinyfish] error scraping {url}: {e}")
        return None


async def scrape_topic(topic: str) -> list[dict]:
    """
    Scrape all sources for a topic in parallel.
    Returns a flat list of articles.
    """
    import asyncio

    sources = get_sources_for_topic(topic)
    print(f"[tinyfish] scraping {len(sources)} sources for '{topic}': {sources}")

    # scrape all sources in parallel
    tasks = [scrape_url(url, topic) for url in sources]
    results = await asyncio.gather(*tasks)

    # flatten into one list
    articles = []
    for result in results:
        if result and result.get("articles"):
            items = result["articles"]
            if isinstance(items, list):
                articles.extend(items)

    print(f"[tinyfish] got {len(articles)} articles for '{topic}'")
    return articles


# ── test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    async def test():
        articles = await scrape_topic("machine learning")
        print(json.dumps(articles, indent=2))

    asyncio.run(test())