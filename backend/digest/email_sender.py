# backend/digest/email_sender.py

import os
import sys
import resend
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")
resend.api_key = os.getenv("RESEND_API_KEY")

async def send_digest_email(to_email: str, html_content: str) -> bool:
    """
    Sends the digest email via Resend.
    Returns True if successful, False if failed.
    """
    try:
        params = {
            "from": "ForYou Digest <onboarding@resend.dev>",
            "to": [to_email],
            "subject": f"Your ForYou Daily Digest",
            "html": html_content
        }

        email = resend.Emails.send(params)
        print(f"[email] sent to {to_email} — id: {email['id']}")
        return True

    except Exception as e:
        print(f"[email] failed to send to {to_email}: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    from digest_builder import build_email_html

    async def test():
        fake_articles = {
            "machine learning": [
                {
                    "title": "GPT-5 Released with Major Improvements",
                    "summary": "OpenAI releases GPT-5 with significantly better reasoning.",
                    "url": "https://techcrunch.com",
                    "source": "TechCrunch"
                }
            ]
        }

        html = build_email_html(
            subscriber_email="gursparshsodhi@gmail.com",
            digest_topics=["machine learning"],
            topic_articles=fake_articles
        )

        success = await send_digest_email("gursparshsodhi@gmail.com", html)
        print("Success!" if success else "Failed!")

    asyncio.run(test())