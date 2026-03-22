# agents/orchestrator_agent.py

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from runner import run_agent

AVAILABLE_AGENTS = {
    "youtube": "Finds relevant YouTube videos. Best for tutorials, talks, and visual content.",
    "hn": "Finds Hacker News stories. Best for tech, programming, startups and software discussion.",
        "news": "Finds recent news articles. Best for current events, science, health, business and general topics.",
}

async def run_orchestrator(user_interest: str) -> dict:
    
    # format the registry nicely for the prompt
    agents_list = "\n".join([f"- {name}: {desc}" for name, desc in AVAILABLE_AGENTS.items()])

    result = await run_agent(
        system_prompt=f"""You are an orchestrator agent. Your job is to read 
            the user's interest and decide which agents to call and what query to 
            give each one.

            Available agents:
            {agents_list}

            Rules:
            - Only select agents that are relevant to the user's interest
            - Tailor each query to suit that agent's platform (e.g. YouTube queries 
            should be video-friendly, Reddit queries should be discussion-friendly)
            - Return ONLY a valid JSON object, no explanation, no markdown, no extra text
            - Format: {{"agent_name": "tailored query for that agent", ...}}

            Example output for "I like machine learning":
            {{"youtube": "machine learning tutorials for beginners", "reddit": "machine learning tips resources discussion"}}""",
        user_message=f"I am interested in content about: {user_interest}",
        tools=None,
        tools_map=None
    )

    # strip markdown code blocks if model wraps it in ```json ... ```
    cleaned = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    # filter out any agents not in AVAILABLE_AGENTS dict
    valid_result = {k: v for k, v in json.loads(cleaned).items() if k in AVAILABLE_AGENTS}
    return valid_result


if __name__ == "__main__":
    import asyncio

    async def test():
        result = await run_orchestrator("indie game development")
        print("Orchestrator output:", result)
        print("Type:", type(result))  # should be dict not string

    asyncio.run(test())