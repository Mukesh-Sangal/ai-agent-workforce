# AI Agent Workforce — Day 1 starter

A learning project for Mukesh Kumar: build a production-oriented agent platform in eight teaching weeks plus four buffer days. Only Day 1 is implemented in this package.

Start with [the roadmap](docs/ROADMAP.md), then [the Day 1 lesson](docs/DAY_01.md). Tests actually performed are recorded in [verification](docs/TEST_RESULTS.md).

## Current behavior

- GET /health reports application liveness.
- POST /task-previews validates and echoes a task description with a UUID.
- No task is persisted, queued or executed. There is no LLM or agent in Day 1.
- The API binds to localhost for the lesson. Authentication arrives before staging deployment.

## Quick start — Ubuntu, Python 3.12

From the extracted ai-agent-workforce directory:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.lock.txt
cd backend
python -m unittest discover -s tests -v
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs and try POST /task-previews. See docs/DAY_01.md for payloads, explanations and troubleshooting. Ctrl+C stops the development server; `--reload` is for local development.

No API key or paid service is needed today. .env.example reserves backend settings for Day 3 and is not loaded by Day 1 code.

## Source map

| Path | Purpose |
|---|---|
| backend/app/__init__.py | Python package marker |
| backend/app/main.py | App, request/response schemas and two routes |
| backend/tests/test_api.py | Nine deterministic API tests |
| backend/requirements.txt | Explicit direct dependency versions, including test client |
| backend/requirements.lock.txt | Full versions from the successful clean installation |
| docs/ROADMAP.md | Architecture, 60 daily tasks and completion gates |
| docs/DAY_01.md | Complete lesson with source code |
| docs/TEST_RESULTS.md | What was and was not verified |
| docs/DAILY_PROGRESS_TEMPLATE.md | Reusable daily evidence template |

Keep .env and virtual environments out of Git. No remote repository has been created or changed by this package.
