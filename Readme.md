# ForYou — AI-Powered Content Discovery

ForYou is a multi-agent AI recommendation system that discovers personalised content across YouTube, Hacker News, and News sources based on your interests. It also sends daily email digests with AI-scraped summaries of the topics you care about.

Built for the Claude Builders Club @ ASU Hackathon 2026.

---

## What it does

- Enter up to 5 interests (e.g. "machine learning", "indie game dev", "climate change")
- A multi-agent AI system searches YouTube, Hacker News, and News in parallel
- An AI ranker scores and merges all results into one unified feed
- Filter by source (All / YouTube / HN / News) with one click
- Subscribe to a daily email digest — AI scrapes the web every morning and sends you a personalised briefing

---

## Architecture

```
User query
    ↓
Orchestrator agent (Qwen3)
    ↓ — decides which agents to call and with what query
[YouTube agent] [HN agent] [News agent]   ← run in parallel
    ↓ — each calls its tools (MCP / API / HTTP)
[YouTube MCP]  [HN Algolia API]  [NewsAPI]
    ↓
Ranker agent (Qwen3) — scores and merges all results
    ↓
React frontend — unified feed with filter pills
```

### Email digest pipeline

```
User subscribes with email + digest topics
    ↓
Daily scheduler (APScheduler, 8am)
    ↓
Tinyfish AI scraper — browses web for each topic in parallel
    ↓
digest_builder.py — formats articles into HTML email
    ↓
Resend — delivers to user's inbox
```

---

## Tech stack

| Layer | Technology |
|---|---|
| LLM | Qwen3-Coder-30B (university hosted, OpenAI-compatible) |
| Agent framework | Custom multi-agent runner (Python asyncio) |
| Tool protocol | MCP (Model Context Protocol) for YouTube |
| YouTube data | YouTube Data API v3 + MCP server |
| HN data | Algolia HN API (no key needed) |
| News data | NewsAPI |
| Web scraping | Tinyfish AI scraper |
| Email | Resend |
| Scheduling | APScheduler |
| Backend | FastAPI + uvicorn |
| Frontend | React + Vite |
| Storage | JSON flat file (subscribers) |

---

## Project structure

```
ForYou-Tube/
├── .env                        # API keys (never commit this)
├── agents/
│   ├── runner.py               # Generic tool call loop — used by all agents
│   ├── orchestrator_agent.py   # Decides which agents to call
│   ├── youtube_agent.py        # Searches YouTube via MCP
│   ├── hn_agent.py             # Searches Hacker News via Algolia API
│   ├── news_agent.py           # Searches news via NewsAPI
│   └── ranker_agent.py         # Scores and merges all results
├── MCP/
│   └── youtube_mcp.py          # MCP server for YouTube Data API
├── backend/
│   ├── main.py                 # FastAPI server + endpoints
│   └── digest/
│       ├── __init__.py
│       ├── tinyfish_scraper.py # Scrapes web via Tinyfish AI
│       ├── digest_builder.py   # Formats HTML email
│       ├── email_sender.py     # Sends via Resend
│       └── scheduler.py        # Daily digest runner
├── frontend/
│   └── src/
│       ├── App.jsx             # Main app — feed + digest panel
│       ├── App.css             # All styles
│       └── VideoCard.jsx       # YouTube card component
└── data/
    └── subscribers.json        # Subscriber storage
```

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- University VPN access (required for Qwen3 endpoint)

### 1. Clone and create virtual environment

```bash
git clone https://github.com/yourusername/ForYou-Tube.git
cd ForYou-Tube
python -m venv myENV
source myENV/bin/activate
```

### 2. Install Python dependencies

```bash
pip install fastapi uvicorn openai mcp google-api-python-client \
            python-dotenv httpx httpx-sse praw resend apscheduler
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
# Qwen3 (university hosted)
QWEN_API_KEY=your_key
QWEN_API_URL=https://your-university-endpoint/v1

# YouTube Data API v3
# Get from console.cloud.google.com → APIs & Services → Credentials
YOUTUBE_API_KEY=your_key

# NewsAPI
# Get from newsapi.org (free tier, 100 req/day)
NEWS_API_KEY=your_key

# Tinyfish AI scraper
# Get from tinyfish.ai
TINYFISH_API_KEY=your_key

# Resend (email)
# Get from resend.com (free tier)
RESEND_API_KEY=your_key

# Reddit (optional, pending API approval)
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=ForYouTube/1.0 by yourusername
```

### 5. Run the backend

```bash
myENV/bin/python -m uvicorn backend.main:app --reload --port 8000
```

### 6. Run the frontend

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/recommend` | Run full agent pipeline for given interests |
| POST | `/subscribe` | Save email + digest topics to subscribers.json |
| POST | `/send-digest` | Trigger digest email immediately (for demo) |
| GET | `/health` | Health check |

### Example request

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"interests": ["machine learning", "indie game dev"]}'
```

---

## How the agent runner works

Every agent in the system uses the same generic tool call loop in `runner.py`:

```
1. Send message + tool schemas to Qwen3
2. Model responds with a tool call (JSON)
3. Your code executes the tool
4. Append result to conversation
5. Loop until model gives final answer
```

This means adding a new agent is just:
- Write the tool function
- Define the tool schema
- Pass both to `run_agent()`

---

## Adding a new source agent

1. Create `agents/new_agent.py` following the HN agent pattern
2. Add to `AVAILABLE_AGENTS` in `orchestrator_agent.py`
3. Add to `AGENT_RUNNERS` in `backend/main.py`
4. Add output schema to `ranker_agent.py` system prompt
5. Add filter pill in `App.jsx`

---

## Ethical considerations

**Filter bubbles** — ForYou searches based on explicit user interests rather than implicit behavioural tracking. Users control exactly what they see and can change it at any time. There is no hidden engagement optimisation.

**Data privacy** — The only personal data stored is email and self-declared interests in a local JSON file. No browsing history, no click tracking, no data sold to third parties.

**Transparency** — Every result is labelled with its source and an AI-generated relevance score so users understand why content was recommended.

**Unsubscribe** — Users can stop email digests at any time. No dark patterns.

**Content quality** — The ranker scores by relevance to the user's stated interest, not by engagement metrics like view count or upvotes. This actively resists optimising for outrage or clickbait.

**Limitations** — The system inherits biases from the underlying sources (YouTube, HN, NewsAPI). Fringe or underrepresented topics may surface lower quality results. Future work would include source diversity scoring.

---

## Future roadmap

- Reddit integration (API approval pending)
- Click feedback loop — learn from what users actually engage with
- Preference memory — system improves recommendations over time
- Source diversity scoring — ensure results aren't all from the same outlet
- User accounts with proper authentication
- Mobile app
- Browser extension for one-click saving

---

## Built with

- [Anthropic MCP](https://modelcontextprotocol.io) — tool protocol
- [Qwen3](https://qwenlm.github.io) — language model
- [Tinyfish](https://tinyfish.ai) — AI web scraper
- [Resend](https://resend.com) — email delivery
- [FastAPI](https://fastapi.tiangolo.com) — backend framework
- [React](https://react.dev) — frontend framework

---

## License

MIT