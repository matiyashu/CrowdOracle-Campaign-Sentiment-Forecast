# CrowdOracle

**Multi-agent marketing intelligence — see the reaction before you ship the campaign.**

CrowdOracle is an
open-source platform that rehearses a marketing campaign against a simulated
audience *before* launch, then ingests the real-world signal after launch and
compares the two. Created and maintained by **Prima Hanura Akbar**.

Licensed under **AGPL-3.0** — free to self-host and fork.

---

## Table of contents

- [What it does](#what-it-does)
- [How it works](#how-it-works)
- [What you can build with it](#what-you-can-build-with-it)
- [Architecture](#architecture)
- [Getting started](#getting-started)
- [Demo mode](#demo-mode)
- [Deploying the frontend to Vercel](#deploying-the-frontend-to-vercel)
- [Author & credits](#author--credits)
- [License](#license)

---

## What it does

CrowdOracle turns an upstream **brief** into a downstream **impact score** by
chaining four things that are usually done in isolation:

1. **Reality Seed** — you upload your brief, brand guide, competitor teardown,
   and any PDFs/decks that describe the world the campaign lives in. The app
   extracts entities (brand, products, creatives, audiences, creators,
   competitors) into a temporal knowledge graph.
2. **Crowd simulation** — it spins up a population of synthetic agents derived
   from that graph and runs them on simulated Twitter + Reddit for N rounds.
   Each agent has beliefs, demographics, and a posting cadence. The run
   produces *posts, replies, reposts, and opinion drift* — exactly what a
   real audience would emit.
3. **Real-world ingestion** — after the campaign launches you upload (or pipe
   in) actual social mentions and paid-performance data. The same entity
   graph indexes them.
4. **Analytics + report** — a ReACT-loop report agent narrates findings
   against both datasets: aspect-level sentiment, keyword shifts, creative
   resonance, topic clusters, and a transparent four-component impact score.
   Every claim links back to the specific node/edge/mention that backs it.

If all you want is the simulation, you can stop after step 2. If all you want
is post-campaign autopsy, you can skip to step 3.

## How it works

```
┌──────────────┐  ontology   ┌─────────────────┐  entity       ┌──────────────┐
│ Upload brief │ ─────────► │ Knowledge graph │ ────────────► │ Agent crowd  │
│ + creatives  │  (LLM +     │ (Zep-backed,    │  filter +     │ (OASIS, dual │
│ + docs       │   vision)   │  temporal)      │  profile      │  platform)   │
└──────────────┘             └─────────────────┘               └──────┬───────┘
                                    ▲                                  │
                                    │                                  ▼
                                    │                         ┌───────────────┐
┌──────────────┐   ingest    ┌─────────────────┐             │ Simulated posts│
│ Real mentions│ ──────────► │ Same graph,     │             │  + opinions   │
│ + perf CSV   │             │  post-launch    │             │   over rounds  │
└──────────────┘             │  snapshot       │             └──────┬───────┘
                             └─────────────────┘                    │
                                    │                                │
                                    ▼                                ▼
                             ┌──────────────────────────────────────────┐
                             │ Analytics: sentiment • keywords •        │
                             │ topics • creative resonance • impact     │
                             │ score (ReACT report agent narrates)      │
                             └──────────────────────────────────────────┘
```

- **LLM routing** — every stage (vision, sentiment, keyword extraction, report
  writing, simulation agents, chat) can use a different model. Configure per-
  task routing in *Settings → Providers*. Built-in adapters: OpenAI, Anthropic
  (Claude), Google (Gemini), Qwen, and any OpenAI-compatible custom endpoint.
- **Knowledge graph** — temporal Zep Cloud graph stores entities, edges, and
  facts with provenance. A demo-mode bypass serves a local JSON snapshot so
  you can run the UI end-to-end without Zep credentials.
- **Simulation engine** — builds on the multi-agent OASIS framework. Each
  agent carries a profile (persona, demographics, topic affinity) derived
  from your graph; the runner steps the population round by round across
  Twitter + Reddit timelines in parallel.
- **Storage** — SQLAlchemy ORM for campaigns, creatives, mentions, and
  performance metrics; flat JSON files under `backend/uploads/` for project
  state, simulation state, and the knowledge-graph snapshot.

## What you can build with it

- **Pre-launch rehearsal** — upload a brief two weeks before ship, run 24
  rounds, read the report, rewrite the angle.
- **Creative A/B forecast** — attach four hero assets to the same brief,
  simulate each, compare sentiment + topic spread.
- **Post-mortem** — ingest real mentions after a launch that underperformed,
  let the report agent explain *what sentiment shifted and why*.
- **Audience discovery** — let the entity graph surface adjacent audience
  segments you hadn't briefed for.
- **Agency deliverable** — self-host for a client, keep their brief and
  creative out of third-party dashboards.

## Architecture

```
backend/   Flask app (Python 3.11+)
           app/api/         REST blueprints (graph, simulation, report,
                            campaign, creatives, analytics, providers, demo)
           app/services/    Domain services + LLM provider registry
           app/models/      SQLAlchemy ORM (Campaign, CreativeAsset,
                            Mention, PerformanceMetric)
           app/demo/        Demo packages + seeder
           uploads/         projects/ · simulations/ · media/ · data/
frontend/  Vue 3 + Vite SPA
           src/views/public/   Landing, Product, Docs, Login
           src/views/app/      AppShell, Campaigns workspace (6 tabs),
                               Reality Seeds workspace (Graph / Entities /
                               Split / Workbench), Graph browser,
                               Settings hub, Demo launcher
           src/components/realityseeds/   D3 force graph, entities panel,
                                          split/workbench layouts
locales/   en.json / zh.json shared by frontend + backend t() helper
```

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows (use source .venv/bin/activate elsewhere)
pip install -r requirements.txt
cp ..\.env.example ..\.env      # then fill in API keys
python run.py                   # listens on :5001
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # listens on :3000, proxies /api/* to :5001
```

### Required environment

Minimum to boot:

- `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL_NAME` — default OpenAI-compatible provider.
- `ZEP_API_KEY` — knowledge graph storage. *Optional if you only run demo mode.*
- `SECRET_KEY` — Flask session.

Optional providers: `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, etc. Configure per-task
routing in **Settings → Providers** once the app is running.

## Demo mode

Want to kick the tires without supplying a brief or Zep credentials?

1. Start the backend + frontend.
2. Open http://localhost:3000 and click **Try the demo**.
3. Load the *Coastline Summer 26* package. The seeder writes one demo project,
   one completed simulation, one 14-entity knowledge graph, plus sample
   campaigns, creatives, mentions, and performance metrics — all prefixed
   `proj_demo_` / `sim_demo_` / `demo_graph_` so a single **Reset demo** button
   wipes everything cleanly.
4. Browse `/app/graph` (cross-project god's-eye view), click into the Reality
   Seed, try the **Entities** tab, then open the campaign to read the report.

## Deploying the frontend to Vercel

The repo ships with a root [`vercel.json`](./vercel.json) that builds only the
Vue app under [`frontend/`](./frontend) and serves it as a SPA (history-mode
fallback included — deep links like `/app/graph` won't 404).

1. Import the GitHub repo into Vercel. No overrides needed — `vercel.json`
   handles the build command, output directory, and rewrites.
2. Set `VITE_API_BASE_URL` in the Vercel project env to the public URL of your
   Flask backend (deploy it separately — Render / Railway / Fly.io are all fine;
   Vercel serverless won't host the simulation workers because runs are
   stateful and multi-round).
3. Deploy. The first visit hits `/` (landing); `/app/*` routes are SPA-
   rewritten to `index.html` so Vue Router can handle them.

Without a backend URL the UI still renders, but any `/api/*` call will fail —
configure the env var before expecting demo mode, Reality Seeds, or graph data
to load.

## Author & credits

- **Creator:** Prima Hanura Akbar
- Crowd simulation builds on the multi-agent **OASIS** framework.
- Temporal knowledge graph is backed by **Zep Cloud**.
- UI is Vue 3 + Vite; analytics layer uses D3 force-directed graphs.

Contributions welcome — open an issue or a PR.

## License

**AGPL-3.0.** Use it, fork it, self-host it. If you run a modified version as a
network service, your users must be able to get the source of your modified
version. See [`LICENSE`](./LICENSE) for the full text.
