# backend/digest/digest_builder.py

from datetime import datetime


def build_email_html(subscriber_email: str, digest_topics: list[str], topic_articles: dict) -> str:
    """
    Builds the HTML email from scraped articles.
    
    topic_articles looks like:
    {
        "machine learning": [
            {"title": "...", "summary": "...", "url": "...", "source": "..."},
        ],
        "Manchester United": [...]
    }
    """

    date_str = datetime.now().strftime("%A, %B %d %Y")

    # ── build article sections ────────────────────────────────────────
    sections_html = ""
    for topic in digest_topics:
        articles = topic_articles.get(topic, [])
        if not articles:
            continue

        articles_html = ""
        for article in articles[:3]:  # max 3 per topic
            articles_html += f"""
            <tr>
                <td style="padding: 16px 0; border-bottom: 1px solid #f0f0f0;">
                    <a href="{article.get('url', '#')}"
                       style="font-size: 15px; font-weight: 600; color: #111;
                              text-decoration: none; line-height: 1.4;
                              display: block; margin-bottom: 6px;">
                        {article.get('title', 'Untitled')}
                    </a>
                    <p style="font-size: 13px; color: #666; margin: 0 0 6px;
                               line-height: 1.5;">
                        {article.get('summary', '')}
                    </p>
                    <span style="font-size: 11px; color: #aaa;">
                        {article.get('source', '')}
                    </span>
                </td>
            </tr>
            """

        sections_html += f"""
        <tr>
            <td style="padding: 24px 0 8px;">
                <p style="font-size: 11px; font-weight: 700; color: #888;
                           text-transform: uppercase; letter-spacing: 1px; margin: 0;">
                    {topic}
                </p>
            </td>
        </tr>
        {articles_html}
        """

    # ── full email HTML ───────────────────────────────────────────────
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background: #f5f5f5; font-family: system-ui, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #f5f5f5; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0"
                           style="background: #ffffff; border-radius: 12px; overflow: hidden;">

                        <!-- header -->
                        <tr>
                            <td style="background: #111; padding: 28px 40px;">
                                <p style="font-size: 22px; font-weight: 700;
                                           color: #ffffff; margin: 0;">
                                    ForYou Daily Digest
                                </p>
                                <p style="font-size: 13px; color: #888; margin: 6px 0 0;">
                                    {date_str}
                                </p>
                            </td>
                        </tr>

                        <!-- intro -->
                        <tr>
                            <td style="padding: 28px 40px 0;">
                                <p style="font-size: 14px; color: #666; margin: 0; line-height: 1.6;">
                                    Here's what's happening in your world today.
                                </p>
                            </td>
                        </tr>

                        <!-- articles -->
                        <tr>
                            <td style="padding: 0 40px;">
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    {sections_html}
                                </table>
                            </td>
                        </tr>

                        <!-- footer -->
                        <tr>
                            <td style="padding: 28px 40px; border-top: 1px solid #f0f0f0;">
                                <p style="font-size: 12px; color: #bbb; margin: 0; text-align: center;">
                                    You're receiving this because you subscribed to ForYou.<br>
                                    To unsubscribe reply with "unsubscribe" to this email.
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return html


# ── test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fake_articles = {
        "machine learning": [
            {
                "title": "GPT-5 Released with Major Improvements",
                "summary": "OpenAI releases GPT-5 with significantly better reasoning capabilities.",
                "url": "https://techcrunch.com",
                "source": "TechCrunch"
            },
            {
                "title": "New Paper on Diffusion Models",
                "summary": "Researchers propose a faster training method for diffusion models.",
                "url": "https://arxiv.org",
                "source": "Papers with Code"
            }
        ],
        "Manchester United": [
            {
                "title": "Man United Beat Arsenal 2-1",
                "summary": "A late Rashford goal secured three points for United at Old Trafford.",
                "url": "https://espn.com",
                "source": "ESPN"
            }
        ]
    }

    html = build_email_html(
        subscriber_email="test@email.com",
        digest_topics=["machine learning", "Manchester United"],
        topic_articles=fake_articles
    )

    # save to a file so you can open it in browser and see how it looks
    with open("test_email.html", "w") as f:
        f.write(html)

    print("Email saved to test_email.html — open it in your browser!")