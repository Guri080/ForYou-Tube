# MCP/reddit_mcp.py

import os
import praw
from pathlib import Path
from dotenv import load_dotenv
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

load_dotenv(Path(__file__).parent.parent / ".env")

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

app = Server("reddit-mcp")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_reddit",
            description="Search Reddit for posts matching a query. Optionally target a specific subreddit.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query e.g. 'indie game dev tips'"
                    },
                    "subreddit": {
                        "type": "string",
                        "description": "Subreddit to search in e.g. 'gamedev'. Leave empty to search all of Reddit.",
                        "default": "all"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of posts to return (max 10)",
                        "default": 5
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order: relevance, hot, top, new",
                        "default": "relevance"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_subreddit_hot",
            description="Get the current hot posts from a specific subreddit. Good for trending content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "subreddit": {
                        "type": "string",
                        "description": "Subreddit name e.g. 'gamedev'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of posts to return (max 10)",
                        "default": 5
                    }
                },
                "required": ["subreddit"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "search_reddit":
        query = arguments["query"]
        subreddit_name = arguments.get("subreddit", "all")
        max_results = arguments.get("max_results", 5)
        sort = arguments.get("sort", "relevance")

        subreddit = reddit.subreddit(subreddit_name)
        posts = subreddit.search(query, sort=sort, limit=max_results)

        results = []
        for post in posts:
            results.append({
                "title": post.title,
                "subreddit": post.subreddit.display_name,
                "url": f"https://reddit.com{post.permalink}",
                "score": post.score,
                "num_comments": post.num_comments,
                "text_preview": post.selftext[:200] if post.selftext else None,
                "external_link": post.url if not post.is_self else None,
                "created_utc": post.created_utc
            })

        return [types.TextContent(type="text", text=str(results))]

    elif name == "get_subreddit_hot":
        subreddit_name = arguments["subreddit"]
        max_results = arguments.get("max_results", 5)

        subreddit = reddit.subreddit(subreddit_name)

        results = []
        for post in subreddit.hot(limit=max_results):
            results.append({
                "title": post.title,
                "subreddit": post.subreddit.display_name,
                "url": f"https://reddit.com{post.permalink}",
                "score": post.score,
                "num_comments": post.num_comments,
                "text_preview": post.selftext[:200] if post.selftext else None,
                "external_link": post.url if not post.is_self else None,
                "created_utc": post.created_utc
            })

        return [types.TextContent(type="text", text=str(results))]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())