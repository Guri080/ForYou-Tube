# backend/digest/scheduler.py

import json
import asyncio
from pathlib import Path
from digest.tinyfish_scraper import scrape_topic
from digest.digest_builder import build_email_html
from digest.email_sender import send_digest_email

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "subscribers.json"


def read_subscribers() -> dict:
    if not DATA_FILE.exists():
        return {}
    return json.loads(DATA_FILE.read_text())


def write_subscribers(data: dict):
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2))


async def send_digest_to_subscriber(email: str, subscriber: dict):
    """Runs the full digest pipeline for one subscriber."""
    digest_topics = subscriber.get("digest_topics", [])
    if not digest_topics:
        print(f"[scheduler] no digest topics for {email}, skipping")
        return

    print(f"[scheduler] building digest for {email} — topics: {digest_topics}")

    # scrape all topics in parallel
    tasks = [scrape_topic(topic) for topic in digest_topics]
    results = await asyncio.gather(*tasks)

    # map topic → articles
    topic_articles = {
        topic: articles
        for topic, articles in zip(digest_topics, results)
    }

    # build email html
    html = build_email_html(
        subscriber_email=email,
        digest_topics=digest_topics,
        topic_articles=topic_articles
    )

    # send it
    await send_digest_email(email, html)


async def run_daily_digest():
    """Sends digest to all subscribers. Called by the scheduler."""
    print("[scheduler] running daily digest...")
    subscribers = read_subscribers()

    if not subscribers:
        print("[scheduler] no subscribers yet")
        return

    tasks = [
        send_digest_to_subscriber(email, data)
        for email, data in subscribers.items()
    ]
    await asyncio.gather(*tasks)
    print(f"[scheduler] done — sent to {len(subscribers)} subscriber(s)")