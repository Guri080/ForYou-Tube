# ForYou — AI-Powered Content Discovery

Every content platform today optimizes for engagement, not for the user. ForYou flips that — you tell it what you want to learn, and a multi-agent AI system finds the best content across YouTube, Hacker News, and News, ranked purely by relevance to what you stated. No behavioral tracking, no hidden signals. A daily email digest scrapes the web each morning and delivers a personalized briefing straight to your inbox. Your feed, your terms.

Built solo in under 24 hours for the Claude Builders Club @ ASU Hackathon 2026.

---

## Features

- Enter up to 5 interests in plain language
- Multi-agent system searches YouTube, HN, and News simultaneously in parallel
- AI ranker scores and merges all results into one unified feed
- Filter feed by source (All / YouTube / HN / News) with one click
- Interest tags on every card so you know why it was recommended
- Daily email digest — AI scrapes the web each morning and sends a personalized briefing to any email address
- Digest topics are separate from feed interests — be as specific as "machine learning research papers" or "Manchester United match results"

---

## Architecture

### Feed pipeline

![image alt](https://github.com/Guri080/ForYou-Tube/blob/c00d5a9d4cd28886d66f47ac226b6bb553d558a5/assests/feed_diag.png)

### Email digest pipeline

![image alt]([https://github.com/Guri080/ForYou-Tube/blob/c00d5a9d4cd28886d66f47ac226b6bb553d558a5/assests/feed_diag.png](https://github.com/Guri080/ForYou-Tube/blob/c00d5a9d4cd28886d66f47ac226b6bb553d558a5/assests/digest_eg.png))

---

## Example

![image_alt](https://github.com/Guri080/ForYou-Tube/blob/c00d5a9d4cd28886d66f47ac226b6bb553d558a5/assests/feed_eg.png)

## Tech Stack

Python, FastAPI, React, Gemini 2.5 Flash-Lite (Vertex AI), MCP Protocol, YouTube Data API, Algolia HN API, NewsAPI, Tinyfish AI Scraper, Gmail SMTP, APScheduler, Google Cloud, Vercel

---

## Project Structure

```
ForYou-Tube/
├── .env                          # API keys (never commit this)
├── agents/
│   ├── runner.py                 # Generic tool call loop — used by all agents
│   ├── orchestrator_agent.py     # Decides which agents to call and with what query
│   ├── youtube_agent.py          # Searches YouTube via MCP server
│   ├── hn_agent.py               # Searches Hacker News via Algolia API
│   ├── news_agent.py             # Searches news via NewsAPI
│   └── ranker_agent.py           # Scores and merges all results
├── MCP/
│   └── youtube_mcp.py            # MCP server wrapping YouTube Data API v3
├── backend/
│   ├── main.py                   # FastAPI server + all endpoints
│   └── digest/
│       ├── __init__.py
│       ├── tinyfish_scraper.py   # Scrapes web via Tinyfish AI
│       ├── digest_builder.py     # Formats HTML email
│       ├── email_sender.py       # Sends via Gmail SMTP
│       └── scheduler.py          # Daily digest runner
├── frontend/
│   └── src/
│       ├── App.jsx               # Main app — unified feed + digest panel
│       ├── App.css               # All styles
│       └── VideoCard.jsx         # YouTube card component
└── data/
    └── subscribers.json          # Subscriber storage
```

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google Cloud account with Vertex AI enabled
- `gcloud` CLI installed and authenticated

### 1. Clone and create virtual environment

```bash
git clone https://github.com/Guri080/ForYou-Tube.git
cd ForYou-Tube
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install fastapi uvicorn openai mcp google-api-python-client \
            python-dotenv httpx httpx-sse apscheduler \
            google-auth google-auth-httplib2
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Configure environment variables

Create a `.env` file in the root:

```bash
# YouTube Data API v3
# Get from console.cloud.google.com → APIs & Services → Credentials
YOUTUBE_API_KEY=your_key

# NewsAPI (free tier, 100 req/day)
# Get from newsapi.org
NEWS_API_KEY=your_key

# Tinyfish AI scraper
# Get from tinyfish.ai
TINYFISH_API_KEY=your_key

# Gmail (for digest emails)
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password

# Reddit (optional, pending API approval)
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=ForYouTube/1.0 by yourusername
```

### 5. Authenticate with Google Cloud (for Gemini via Vertex AI)

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project your-project-id
```

### 6. Run the backend

```bash
myENV/bin/python -m uvicorn backend.main:app --reload --port 8000
```

### 7. Run the frontend

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/recommend` | Run full agent pipeline for given interests |
| POST | `/subscribe` | Save email + digest topics |
| POST | `/send-digest` | Trigger digest email immediately |
| GET | `/health` | Health check |

### Example request

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"interests": ["machine learning", "indie game dev", "climate change"]}'
```

---

## How the Agent Runner Works

Every agent uses the same generic tool call loop in `runner.py`:

```
1. Send message + tool schemas to Gemini
2. Model responds with a tool call (JSON)
3. Your code executes the tool
4. Append result to conversation history
5. Loop until model gives final text answer
```

The runner is model-agnostic — swap the endpoint and model name and it works with any OpenAI-compatible API.

---

## Adding a New Source Agent

1. Create `agents/new_agent.py` following the HN agent pattern
2. Add to `AVAILABLE_AGENTS` in `orchestrator_agent.py`
3. Add to `AGENT_RUNNERS` in `backend/main.py`
4. Add output schema to `ranker_agent.py` system prompt
5. Add filter pill in `App.jsx`
6. Done — the orchestrator automatically learns the new source exists

---

## Ethical Considerations

**No engagement optimization** — results are ranked by relevance to stated interest, not by view count, likes, or platform engagement metrics. This actively resists optimising for outrage or clickbait.

**Explicit intent only** — the system only uses what the user explicitly types. No behavioral tracking, no click history, no implicit signals.

**Full user control** — users choose their feed interests and digest topics independently. Both can be changed at any time. Nothing is inferred or assumed.

**Transparency** — every result shows its source, interest tag, and AI relevance score so users understand exactly why content was recommended.

**No dark patterns** — the digest delivers once to the inbox and leaves. No notification systems designed to pull users back in.

**Data privacy** — the only personal data stored is email and self-declared topics in a local JSON file. No data is sold or shared.

**Limitations** — the system inherits biases from underlying sources (YouTube, HN, NewsAPI). Niche or underrepresented topics may surface lower quality results. Future work includes source diversity scoring.

---

## Future Roadmap

- Reddit integration (API approval pending)
- Click feedback loop — learn from what users actually engage with, always based on stated intentions
- Preference memory — system improves recommendations over time
- Source diversity scoring — prevent all results coming from one outlet
- User accounts with proper authentication and a real database
- Mobile app

---

## Deployment

**Frontend** — deployed on Vercel at `for-you-tube.vercel.app`

**Backend** — runs on Google Cloud Compute Engine (e2-medium, us-central1-a) with Cloudflare Tunnel for HTTPS

To stop the GCP VM (stops billing):
```bash
gcloud compute instances stop foryou-backend \
  --project=your-project-id \
  --zone=us-central1-a
```

---

## Built With

- [Gemini 2.5 Flash-Lite](https://cloud.google.com/vertex-ai) — language model via Vertex AI
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io) — tool integration standard
- [Tinyfish](https://tinyfish.ai) — AI web scraper for digest content
- [FastAPI](https://fastapi.tiangolo.com) — backend framework
- [React](https://react.dev) + [Vite](https://vitejs.dev) — frontend
- [Vercel](https://vercel.com) — frontend hosting
- [Google Cloud](https://cloud.google.com) — backend hosting

---

## License

MIT
