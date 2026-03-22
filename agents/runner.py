# agents/runner.py

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(Path(__file__).parent.parent / ".env")

client = AsyncOpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url=os.getenv("QWEN_API_URL")
)

MODEL = "qwen3-coder-30b-a3b-instruct"
MAX_ITERATIONS = 10   # loop limit


async def run_agent(
    system_prompt: str,
    user_message: str,
    tools: list = None,       # list of tool schemas (JSON)
    tools_map: dict = None    # {"tool_name": callable_function}
) -> str:

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message}
    ]

    for iteration in range(MAX_ITERATIONS):

        # ── call the model ────────────────────────────────────────────
        kwargs = {"model": MODEL, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"   # model decides when to call tools

        response = await client.chat.completions.create(**kwargs)
        response_message = response.choices[0].message

        # ── no tool call -> model is done, return final answer ─────────
        if not response_message.tool_calls:
            return response_message.content

        # ── tool call -> execute each one and loop back ────────────────
        messages.append(response_message)   # append assistant's tool request

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"[runner] calling tool: {tool_name} with {tool_args}")

            if tool_name in tools_map:
                tool_result = await tools_map[tool_name](**tool_args)
            else:
                tool_result = f"Error: tool '{tool_name}' not found"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })

    return "Error: max iterations reached"

async def test():
    '''
    Testing file to check the working of script
    '''
    result = await run_agent(
        system_prompt="You are a helpful assistant.",
        user_message="Say hello in one sentence.",
        tools=None,
        tools_map=None
    )
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())