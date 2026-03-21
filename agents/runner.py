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
MAX_ITERATIONS = 10


async def run_agent(
    system_prompt: str,
    user_message: str,
    tools: list = None,       # list of tool schemas in OpenAI format
    tools_map: dict = None    # {"tool_name": callable_function}
) -> str:

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message}
    ]

    for iteration in range(MAX_ITERATIONS):
        print(f"\n[runner] iteration {iteration + 1}")

        # ── build the request ─────────────────────────────────────────
        kwargs = {"model": MODEL, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await client.chat.completions.create(**kwargs)
        response_message = response.choices[0].message

        # ── no tool call → model is done ─────────────────────────────
        if not response_message.tool_calls:
            print("[runner] model gave final answer")
            return response_message.content

        # ── tool call → execute and loop back ────────────────────────
        print(f"[runner] model wants {len(response_message.tool_calls)} tool call(s)")
        messages.append(response_message)  # append assistant message first

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id

            # parse arguments safely
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            print(f"[runner] → {tool_name}({tool_args})")

            # execute the tool
            if tools_map and tool_name in tools_map:
                try:
                    tool_result = await tools_map[tool_name](**tool_args)
                    print(f"[runner] ✓ got result")
                except Exception as e:
                    tool_result = f"Error executing tool: {str(e)}"
                    print(f"[runner] ✗ tool error: {e}")
            else:
                tool_result = f"Error: tool '{tool_name}' not found"
                print(f"[runner] ✗ tool not found")

            # append result back to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": str(tool_result)
            })

    return "Error: max iterations reached without a final answer"


if __name__ == "__main__":
    import asyncio

    async def test():
        result = await run_agent(
            system_prompt="You are a helpful assistant.",
            user_message="Say hello in one sentence."
        )
        print("\nFinal answer:", result)

    asyncio.run(test())