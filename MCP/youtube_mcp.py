# mcp_servers/youtube_mcp.py

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# This is the MCP server instance
app = Server("youtube-mcp")


# ── Tool 1: search videos ─────────────────────────────────────────────
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_youtube",
            description="Search YouTube for videos matching a query. Returns title, channel, views, url, and a short description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query e.g. 'indie game dev tutorials'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return (max 10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_video_details",
            description="Get full details for a specific YouTube video by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_id": {
                        "type": "string",
                        "description": "The YouTube video ID e.g. 'dQw4w9WgXcQ'"
                    }
                },
                "required": ["video_id"]
            }
        )
    ]


# ── Tool execution ─────────────────────────────────────────────────────
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "search_youtube":
        query = arguments["query"]
        max_results = arguments.get("max_results", 5)

        response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            order="relevance"
        ).execute()

        results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            results.append({
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "description": snippet["description"][:200],
                "url": f"https://youtube.com/watch?v={video_id}",
                "video_id": video_id,
                "published_at": snippet["publishedAt"]
            })

        return [types.TextContent(type="text", text=str(results))]

    elif name == "get_video_details":
        video_id = arguments["video_id"]

        response = youtube.videos().list(
            id=video_id,
            part="snippet,statistics"
        ).execute()

        items = response.get("items", [])
        if not items:
            return [types.TextContent(type="text", text="Video not found")]

        item = items[0]
        details = {
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "description": item["snippet"]["description"][:500],
            "views": item["statistics"].get("viewCount", "N/A"),
            "likes": item["statistics"].get("likeCount", "N/A"),
            "url": f"https://youtube.com/watch?v={video_id}"
        }

        return [types.TextContent(type="text", text=str(details))]


# ── Run the server ─────────────────────────────────────────────────────
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())