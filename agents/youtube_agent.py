# agents/youtube_agent.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))  # so we can import runner

from runner import run_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_SERVER_PATH = str(Path(__file__).parent.parent / "MCP" / "youtube_mcp.py")


# ── MCP bridge ────────────────────────────────────────────────────────
async def call_mcp_tool(tool_name: str, tool_args: dict) -> str:
    server_params = StdioServerParameters(
        command="python",
        args=[MCP_SERVER_PATH]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return result.content[0].text


# ── tool functions ────────────────────────────────────────────────────
async def search_youtube(query: str, max_results: int = 5) -> str:
    return await call_mcp_tool("search_youtube", {
        "query": query,
        "max_results": max_results
    })

async def get_video_details(video_id: str) -> str:
    return await call_mcp_tool("get_video_details", {
        "video_id": video_id
    })


# ── tool schemas ──────────────────────────────────────────────────────
YOUTUBE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Search YouTube for videos matching a query. Returns title, channel, url and description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query e.g. 'indie game dev tutorials'"
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_video_details",
            "description": "Get full details for a specific YouTube video by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "video_id": {
                        "type": "string",
                        "description": "The YouTube video ID e.g. 'dQw4w9WgXcQ'"
                    }
                },
                "required": ["video_id"]
            }
        }
    }
]

YOUTUBE_TOOLS_MAP = {
    "search_youtube": search_youtube,
    "get_video_details": get_video_details
}


# ── the agent ─────────────────────────────────────────────────────────
async def run_youtube_agent(user_interest: str) -> str:
    return await run_agent(
        system_prompt="""You are the YouTube agent. Your job is to find 
        relevant YouTube videos based on the user's interests.
        Search for videos, get details on the most promising ones, 
        and return a structured list of the top 5 results.
        Always return results as a JSON list with fields:
        title, channel, url, description, video_id.""",
        user_message=f"Find YouTube videos about: {user_interest}",
        tools=YOUTUBE_TOOLS,
        tools_map=YOUTUBE_TOOLS_MAP
    )


# ── test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    async def test():
        print("Running YouTube agent...")
        result = await run_youtube_agent("indie game development")
        print("\nResult:")
        print(result)

    asyncio.run(test())