# backend/main.py

import sys
import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# ── path setup first, before ANY local imports ────────────────────────
sys.path.append(str(Path(__file__).parent.parent / "agents"))
sys.path.append(str(Path(__file__).parent))

# ── local imports after path is set ──────────────────────────────────
from digest.scheduler import run_daily_digest, read_subscribers, write_subscribers, send_digest_to_subscriber
from orchestrator_agent import run_orchestrator
from youtube_agent import run_youtube_agent
from ranker_agent import run_ranker_agent
from hn_agent import run_hn_agent
from news_agent import run_news_agent

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    scheduler.add_job(
        run_daily_digest,
        CronTrigger(hour=8, minute=0),
        id="daily_digest"
    )
    scheduler.start()
    print("[backend] scheduler started — digest runs daily at 8am")
    yield
    # shutdown
    scheduler.shutdown()
    print("[backend] scheduler stopped")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── request models ────────────────────────────────────────────────────
class RecommendRequest(BaseModel):
    interests: List[str]

class SubscribeRequest(BaseModel):
    email: str
    digest_topics: list[str]
    feed_interests: list[str] = []

AGENT_RUNNERS = {
    "youtube": run_youtube_agent,
    "hn": run_hn_agent,
    "news": run_news_agent,
}

# ── pipeline ──────────────────────────────────────────────────────────
async def run_pipeline_for_interest(interest: str) -> list:
    print(f"[backend] running pipeline for: '{interest}'")

    agent_plan = await run_orchestrator(interest)
    print(f"[backend] agent plan for '{interest}': {agent_plan}")

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
    return [r for r in results if r is not None]


# ── endpoints ─────────────────────────────────────────────────────────
@app.post("/recommend")
async def recommend(request: RecommendRequest):
    interests = [i.strip() for i in request.interests if i.strip()]
    if not interests:
        raise HTTPException(status_code=400, detail="At least one interest required")
    if len(interests) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 interests allowed")

    print(f"\n[backend] new request with {len(interests)} interest(s): {interests}")

    pipeline_tasks = [run_pipeline_for_interest(interest) for interest in interests]
    all_pipeline_results = await asyncio.gather(*pipeline_tasks)

    tagged_results = []
    for pipeline_result in all_pipeline_results:
        tagged_results.extend(pipeline_result)

    print(f"[backend] sending {len(tagged_results)} result groups to ranker")
    ranked_feed = await run_ranker_agent(tagged_results)
    print("[backend] done!")

    return ranked_feed


@app.post("/subscribe")
async def subscribe(request: SubscribeRequest):
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email")

    digest_topics = [t.strip() for t in request.digest_topics if t.strip()]
    if not digest_topics:
        raise HTTPException(status_code=400, detail="At least one digest topic required")

    subscribers = read_subscribers()
    subscribers[request.email] = {
        "email": request.email,
        "digest_topics": digest_topics,
        "feed_interests": request.feed_interests,
        "subscribed_at": str(__import__("datetime").datetime.now())
    }
    write_subscribers(subscribers)

    print(f"[backend] new subscriber: {request.email} — topics: {digest_topics}")
    return {"success": True, "message": "Subscribed! You'll receive your first digest tomorrow at 8am."}


@app.post("/send-digest")
async def send_digest_now(request: SubscribeRequest):
    subscribers = read_subscribers()

    if request.email not in subscribers:
        raise HTTPException(status_code=404, detail="Email not found. Please subscribe first.")

    await send_digest_to_subscriber(request.email, subscribers[request.email])
    return {"success": True, "message": "Digest sent! Check your inbox."}


@app.get("/health")
async def health():
    return {"status": "ok"}