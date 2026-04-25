# CrowdOracle — agent guidance

CrowdOracle is an open-source (AGPL-3.0) marketing-intelligence platform.
Frontend: Vue 3 + Vite SPA. Backend: Flask + SQLAlchemy + file-backed
project/simulation state under `backend/uploads/`. Knowledge graph runs on
Zep Cloud, with a demo bypass that serves a local JSON snapshot.

## Build/run conventions

- Backend venv lives at `backend/.venv/`. Run with
  `backend/.venv/Scripts/python.exe backend/run.py` (Windows). Listens on `:5001`.
- Frontend dev server: `cd frontend && npm run dev` → `:3000`, proxies `/api/*` to `:5001`.
- Frontend production build: `cd frontend && npm run build`. Run this after
  every frontend change to catch type/syntax issues before committing.
- Vercel deploys the SPA only. Backend must be hosted separately
  (Render / Railway / Fly.io). Vercel env var `VITE_API_BASE_URL` must
  point at the backend's public URL.

## Demo isolation

- Demo project IDs are prefixed `proj_demo_`, simulations `sim_demo_`,
  graph IDs `demo_graph_`. The graph endpoint short-circuits the
  `demo_graph_` prefix to read a local JSON snapshot — never calls Zep
  for demo seeds.
- Demo campaigns carry `"demo"` in `Campaign.tags`. Reset endpoint must
  purge both DB rows and `backend/uploads/{projects,simulations}/<demo_*>`
  directories.

## Behavioral guidelines (always apply)

This project ships with the **karpathy-guidelines** skill at
`.claude/skills/karpathy-guidelines/SKILL.md`. It is non-negotiable for
any code change in this repo:

1. **Think before coding** — surface assumptions, ask when unclear,
   present alternatives instead of picking silently.
2. **Simplicity first** — minimum code that solves the stated problem;
   no speculative abstractions, configs, or error handling for
   impossible cases.
3. **Surgical changes** — every changed line must trace to the user's
   request. Don't "improve" adjacent code, reformat unrelated regions,
   or refactor working code unprompted.
4. **Goal-driven execution** — define a verifiable success criterion
   before starting, then loop until it's met (build passes, smoke test
   passes, endpoint returns expected shape).

Read `.claude/skills/karpathy-guidelines/SKILL.md` if any of these are
unclear in context.

## Repository layout (quick reference)

```
backend/app/api/        REST blueprints — graph, simulation, demo, campaign,
                        creatives, analytics, providers, report
backend/app/services/   Domain services + LLM provider registry
backend/app/models/     SQLAlchemy ORM (Campaign / CreativeAsset / Mention /
                        PerformanceMetric)
backend/app/demo/       Demo packages + seeder; reality-seed materialization
frontend/src/views/app/             AppShell, Campaigns workspace, Reality
                                    Seeds workspace, Graph browser, Demo
frontend/src/components/realityseeds/   GraphPanel (D3), EntitiesPanel,
                                        SplitPanel, WorkbenchPanel
locales/                en.json / zh.json shared by frontend + backend t() helper
```
