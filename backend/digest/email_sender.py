# backend/digest/email_sender.py

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


async def send_digest_email(to_email: str, html_content: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your ForYou Daily Digest"
        msg["From"] = f"ForYou <{GMAIL_USER}>"
        msg["To"] = to_email

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        print(f"[email] sent to {to_email}")
        return True

    except Exception as e:
        print(f"[email] failed to send to {to_email}: {e}")
        return False


if __name__ == "__main__":
    import asyncio

    async def test():
        success = await send_digest_email(
            "gursparshsodhi@gmail.com",
            "<h1>Test email from ForYou!</h1><p>Gmail SMTP is working.</p>"
        )
        print("Success!" if success else "Failed!")

    asyncio.run(test())