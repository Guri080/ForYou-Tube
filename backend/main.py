# backend/main.py

import sys
import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

sys.path.append(str(Path(__file__).parent.parent / "agents"))

from orchestrator_agent import run_orchestrator
from youtube_agent import run_youtube_agent
from ranker_agent import run_ranker_agent
from hn_agent import run_hn_agent
from news_agent import run_news_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── request now takes a list of interests ─────────────────────────────
class RecommendRequest(BaseModel):
    interests: List[str]

AGENT_RUNNERS = {
    "youtube": run_youtube_agent,
    "hn": run_hn_agent,
    "news": run_news_agent,
}

# ── run the full pipeline for one interest ────────────────────────────
async def run_pipeline_for_interest(interest: str) -> list:
    """
    Runs orchestrator + agents for a single interest.
    Returns a list of tagged result dicts ready for the ranker.
    """
    print(f"[backend] running pipeline for: '{interest}'")

    # orchestrator decides which agents to call
    agent_plan = await run_orchestrator(interest)
    print(f"[backend] agent plan for '{interest}': {agent_plan}")

    # run all planned agents in parallel
    async def run_single_agent(agent_name: str, query: str):
        if agent_name not in AGENT_RUNNERS:
            return None
        print(f"[backend] starting {agent_name} agent for '{interest}'...")
        result = await AGENT_RUNNERS[agent_name](query)
        print(f"[backend] {agent_name} done for '{interest}'")
        return {
            "interest": interest,
            "source": agent_name,
            "items": result
        }

    tasks = [
        run_single_agent(agent_name, query)
        for agent_name, query in agent_plan.items()
    ]
    results = await asyncio.gather(*tasks)

    # filter out any None results
    return [r for r in results if r is not None]


# ── the main endpoint ─────────────────────────────────────────────────
@app.post("/recommend")
async def recommend(request: RecommendRequest):

    # validate
    interests = [i.strip() for i in request.interests if i.strip()]
    if not interests:
        raise HTTPException(status_code=400, detail="At least one interest required")
    if len(interests) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 interests allowed")

    print(f"\n[backend] new request with {len(interests)} interest(s): {interests}")

    # run full pipeline for ALL interests in parallel
    pipeline_tasks = [run_pipeline_for_interest(interest) for interest in interests]
    all_pipeline_results = await asyncio.gather(*pipeline_tasks)

    # flatten into one list for the ranker
    tagged_results = []
    for pipeline_result in all_pipeline_results:
        tagged_results.extend(pipeline_result)

    print(f"[backend] sending {len(tagged_results)} result groups to ranker")

    # ranker scores everything and returns structured feed
    ranked_feed = await run_ranker_agent(tagged_results)
    print("[backend] done!")

    return ranked_feed


@app.get("/health")
async def health():
    return {"status": "ok"}