# BigBrother — Campaign Sentiment Forecast

A marketing campaign impact intelligence platform built on top of a multi-agent crowd
simulation engine. Upload a brief, run a simulated audience, ingest real-world
mentions and performance data, and get a transparent impact score with
sentiment, keyword, and creative-resonance breakdowns.

Created by **Prima Hanura Akbar**.

---

## What it does

- **Campaign ingestion** — define a campaign (brand, objective, markets, channels, dates).
- **Creative library** — upload images, video, copy and landing pages; OCR + vision +
  transcript extraction; structured tagging.
- **Mention & performance ingestion** — CSV/XLSX import for social mentions and paid
  performance metrics.
- **Crowd simulation** — agent-based dual-platform (Twitter + Reddit) simulation of how
  the campaign would land with a synthetic audience derived from your knowledge graph.
- **Analytics dashboard** — keyword/phrase frequency, aspect-level sentiment, topic
  clusters, creative breakdown, and a transparent four-component impact score.
- **Report builder** — ReACT-loop report agent that narrates findings and links back to
  source facts in the knowledge graph.
- **Multi-provider LLM settings** — OpenAI, Anthropic, Qwen, Gemini, or any
  OpenAI-compatible custom endpoint, with per-task model routing
  (creative_vision, sentiment, report_writer, simulation, transcript, chat,
  keyword, impact).

## Architecture

```
backend/   Flask app (Python 3.11+)
            api/         REST blueprints (graph, simulation, report, campaign,
                         creatives, analytics, providers)
            services/    Domain services + LLM provider registry
            models/      SQLAlchemy ORM
            uploads/     Media + tabular ingestion folders
frontend/  Vue 3 + Vite SPA with vue-i18n and D3 dashboards
locales/   en.json / zh.json shared by frontend + backend t() helper
```

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows (use source .venv/bin/activate elsewhere)
pip install -r requirements.txt
cp ..\.env.example ..\.env       # then fill in API keys
python run.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api/*` to the Flask backend.

### Required environment

Minimum to boot:

- `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME` — default OpenAI-compatible provider.
- `ZEP_API_KEY` — knowledge graph storage.
- `SECRET_KEY` — Flask session.

Optional providers: `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc. Configure per-task
routing in **Settings → Providers** once the app is running.

## Deploying the frontend to Vercel

The repo ships with a root [`vercel.json`](./vercel.json) that builds only the
Vue app under [`frontend/`](./frontend) and serves it as a SPA (history-mode
fallback included — deep links like `/app/graph` won't 404).

1. Import the GitHub repo into Vercel. No overrides needed — `vercel.json`
   handles the build command, output dir, and rewrites.
2. Set `VITE_API_BASE_URL` in the Vercel project env to the public URL of your
   Flask backend (deploy it separately — Render / Railway / Fly.io are all fine;
   Vercel serverless won't host the simulation workers).
3. Deploy. The first visit hits `/` (landing); `/app/*` routes are SPA-rewritten
   to `index.html` so Vue Router can handle them.

Without a backend URL the UI still renders, but any `/api/*` call will fail —
configure the env var before expecting demo mode, Reality Seeds, or graph data
to load.

## Author & credits

- **Creator:** Prima Hanura Akbar
- The underlying crowd simulation engine builds on the multi-agent OASIS framework
  and a Zep Cloud-backed temporal knowledge graph.

## License

AGPL-3.0
