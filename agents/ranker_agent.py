# agents/ranker_agent.py

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from runner import run_agent

async def run_ranker_agent(tagged_results: list) -> dict:
    """
    tagged_results is a list of dicts like:
    [
        {
            "interest": "machine learning",
            "source": "youtube",
            "items": [...]
        },
        {
            "interest": "indie game dev",
            "source": "youtube",
            "items": [...]
        }
    ]
    """

    ranked = await run_agent(
        system_prompt="""You are a ranker agent. You will be given content results 
        from multiple sources, each tagged with the interest they were fetched for.

        Your job is to:
        - Score each item from 0-10 based on how relevant it is to ITS OWN interest
        - Each item must be scored against its specific interest, not a combined query
        - Keep only the top 5 items per source across all interests combined
        - Sort all items by score descending
        - Construct YouTube thumbnail URLs using:
          https://img.youtube.com/vi/{video_id}/maxresdefault.jpg

        Return ONLY a valid JSON object, no explanation, no markdown, no extra text.

        Format:
        {
            "youtube": [
                {
                    "title": "video title",
                    "url": "https://youtube.com/watch?v=VIDEO_ID",
                    "thumbnail": "https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg",
                    "channel": "channel name",
                    "interest": "the interest this was fetched for",
                    "score": 9.2
                }
            ],
            "reddit": [
                {
                    "title": "post title",
                    "url": "https://reddit.com/r/...",
                    "description": "one sentence preview",
                    "subreddit": "subreddit name",
                    "interest": "the interest this was fetched for",
                    "score": 8.5
                }
            ]
            "hn": [
                {
                    "title": "story title",
                    "url": "external article url or hn url",
                    "hn_url": "https://news.ycombinator.com/item?id=...",
                    "points": 420,
                    "author": "username",
                    "interest": "the interest this was fetched for",
                    "score": 8.1
                }
            ]
            "news": [
                {
                    "title": "article title",
                    "description": "one sentence summary",
                    "url": "https://...",
                    "thumbnail": "https://... or null if no image",
                    "source": "BBC News",
                    "interest": "the interest this was fetched for",
                    "score": 8.3
                }
            ]
        }
        Only include sources that have results.""",
        user_message=f"""## Tagged results from all agents:
{json.dumps(tagged_results, indent=2)}""",
        tools=None,
        tools_map=None
    )

    cleaned = ranked.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


if __name__ == "__main__":
    import asyncio

    async def test():
        fake_tagged_results = [
            {
                "interest": "machine learning",
                "source": "youtube",
                "items": [
                    {"title": "Machine Learning for Beginners", "channel": "freeCodeCamp",
                     "url": "https://youtube.com/watch?v=abc123", "video_id": "abc123",
                     "description": "Full ML course for beginners"},
                    {"title": "Neural Networks Explained", "channel": "3Blue1Brown",
                     "url": "https://youtube.com/watch?v=def456", "video_id": "def456",
                     "description": "Visual explanation of neural networks"}
                ]
            },
            {
                "interest": "indie game development",
                "source": "youtube",
                "items": [
                    {"title": "Indie game dev for beginners", "channel": "SonderingEmily",
                     "url": "https://youtube.com/watch?v=GLijE8KoQjU", "video_id": "GLijE8KoQjU",
                     "description": "Beginner guide to indie game dev"},
                    {"title": "What 4 Years of Solo Indie Game Dev Looks Like", "channel": "zagawee",
                     "url": "https://youtube.com/watch?v=ptvSKUPl5nM", "video_id": "ptvSKUPl5nM",
                     "description": "Solo dev journey"}
                ]
            }
        ]

        result = await run_ranker_agent(fake_tagged_results)
        print(json.dumps(result, indent=2))

    asyncio.run(test())