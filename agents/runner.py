# agents/runner.py

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
import google.auth
import google.auth.transport.requests
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
    Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
)

load_dotenv(Path(__file__).parent.parent / ".env")

def get_fresh_client():
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    
    project_id = project or "foryou-tube"  # fallback to hardcoded if None
    
    return AsyncOpenAI(
        api_key=credentials.token,
        base_url=f"https://us-central1-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/us-central1/endpoints/openapi/"
    )

MODEL = "google/gemini-2.5-flash-lite"
MAX_ITERATIONS = 10


async def run_agent(
    system_prompt: str,
    user_message: str,
    tools: list = None,
    tools_map: dict = None
) -> str:

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message}
    ]

    for iteration in range(MAX_ITERATIONS):
        print(f"\n[runner] iteration {iteration + 1}")

        kwargs = {"model": MODEL, "messages": messages}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # get fresh client each call so token never expires
        client = get_fresh_client()
        response = await client.chat.completions.create(**kwargs)
        response_message = response.choices[0].message

        if not response_message.tool_calls:
            print("[runner] model gave final answer")
            return response_message.content

        print(f"[runner] model wants {len(response_message.tool_calls)} tool call(s)")
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id

            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            print(f"[runner] → {tool_name}({tool_args})")

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