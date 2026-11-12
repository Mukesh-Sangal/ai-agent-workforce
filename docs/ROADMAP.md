# AI Agent Workforce — 60-day roadmap

Prepared for Mukesh Kumar on 12 November 2026. Day numbers are relative; start when ready.

## Goal and schedule

Build a production-oriented portfolio MVP and become able to explain, extend, test and operate it independently. This is a focused learning target, not a guarantee of production readiness or senior-level expertise in 60 days.

Days 1–56 contain eight teaching weeks: six build days of six hours, followed by one optional review/rest day. That is 48 build sessions, about 288 hours. Days 57–60 are recovery, finalization and presentation buffers. If only five build days are available, use a buffer or extend the calendar instead of skipping a prerequisite.

On each build day: hour 1 concepts and official docs; hour 2 a small exercise; hours 3–4 project implementation; hour 5 tests and debugging; hour 6 notes, commit and company demo. Move to the next major concept only after explaining the current one and showing its acceptance checks.

## Starting assessment

Self-reported strengths: frontend development, React/Next.js, JavaScript, APIs and Git. Basic Python is the starting point. Python packaging, async I/O, SQL transactions, LLM APIs, orchestration, evaluations and application security need assessment. Do not infer proficiency from years of employment.

Before Day 2, answer:
1. Explain a browser → backend → external API request, including where secrets belong.
2. Translate a JavaScript function that trims a string into Python and explain indentation and return.
3. What happens when an awaited network call fails? How does that differ from validation failure?
4. Have you created a Python virtual environment and installed dependencies?
5. What is the difference between an LLM generating a tool request and the application executing it?
6. Have you used SQL joins, migrations or database transactions? Give one example, or say new to me.
7. Which steps of Day 1 worked on your machine? Include Python version, actual test output and errors with secrets removed. An approximate daily API budget will help select a model on Day 3.

## Focused end-to-end use cases

Primary workflow: “Research accessible contact-form patterns, propose a React component, test it, and document the result.” The Developer produces a patch/artifact in a dedicated workspace; it does not modify an employer repository. QA reports actual tool executions separately from model review. Humans approve any privileged action.

Secondary workflow: “Analyze this synthetic website-enquiries CSV and explain trends.” Deterministic Python computes values; the model explains verified results. Start with synthetic or authorized data.

Each specialist has its own instructions, input/output schema, tool allowlist and context. Start with bounded sequential execution. Add parallelism only for independent subtasks. Multi-agent collaboration is through typed state and referenced artifacts, not unrestricted chat. A single provider/model can serve multiple roles. Roles need not be separate servers or different models.

## Architecture target

- Frontend: Next.js App Router, JavaScript and Tailwind; dark dashboard, task composer, execution timeline, artifacts, knowledge, history, approvals and usage screens. Use the current stable release verified when installed; commit the lockfile. Do not inherit an older Next.js version automatically.
- Backend: FastAPI owns business rules, authorization, tool policies and the OpenAI integration. Pydantic validates boundaries. All OpenAI credentials stay on the backend.
- Model adapter: use the OpenAI Responses API with a configurable model, structured outputs, tool calls, timeouts and bounded retries. Confirm the selected model supports required features when implementing.
- Persistence: PostgreSQL, SQLAlchemy and Alembic. Prefer SQLAlchemy over Prisma because Python owns application data; one ORM and migration owner avoids duplicate schemas.
- Retrieval: PostgreSQL plus pgvector. Retain document IDs, versions, chunk IDs, source locations and workspace ownership. Retrieved content is untrusted data, never instructions. Begin with exact vector search; optimize only after measuring.
- Execution: FastAPI accepts a run and durably enqueues it; a separate Python worker executes LangGraph. Start with a PostgreSQL jobs table and transactional claim/lease, heartbeat and deduplication. A small MVP does not need an extra Redis service. LangGraph checkpoints capture graph state; they do not replace job scheduling, worker leases or an audit trail.
- Tools: allowlisted search/document retrieval, artifact writing, deterministic CSV calculations and an isolated test runner. No arbitrary shell or SQL from a model. Generated code executes only in a dedicated restricted sandbox with resource limits, no production credentials, no Docker socket and restricted network access. App Docker Compose is not the security boundary for untrusted code.
- Artifacts: local development directory first, object storage by deployment. Store metadata and ownership in PostgreSQL; do not put large files into graph state.
- Observability: structured logs, run/node/tool IDs, timings, token usage, estimated costs and error categories. Keep private input and secrets out of default logs.
- Authentication: an established OIDC provider; FastAPI validates issuer, audience, signature and expiry and enforces workspace roles and object ownership. Never trust a user ID sent in a request body. Before public deployment, test cross-user isolation across runs, events, artifacts, memory, retrieval and approvals.
- Deployment: Docker Compose locally; Next.js web, FastAPI API, independent worker, managed PostgreSQL and artifact storage in staging. CI runs deterministic tests; live-model smoke/evaluation jobs are opt-in and budgeted. Deployment provider chosen in Week 8 from cost, worker support and network requirements.

Request lifecycle: authenticate → validate task → create run and queue job → Manager creates typed bounded plan → validate dependencies and tool permissions → specialists execute → QA checks evidence → approval gate when needed → compile final report. Persist task status and graph checkpoints throughout; stream public execution events to the UI using SSE, with reconnect and polling fallback.

Core entities: users, workspaces, memberships, tasks, runs, jobs, subtasks, messages, artifacts, tool_calls, approvals, documents, chunks, memories and usage_records. Graph checkpoint tables are owned by the chosen checkpointer. Long-term memories are scoped records with retention/deletion controls; run state is short-term execution memory; RAG is source-grounded retrieval.

State should contain run_id, workspace_id, plan, completed steps, artifact references, evidence references, error records, approval references, counters and budgets. An inter-agent message contains schema_version, run_id, subtask_id, sender, recipient, status, artifact_refs and evidence_refs. Show decisions, tool inputs/results and evidence in the dashboard, rather than private chain-of-thought.

Task states: queued, running, awaiting_approval, succeeded, failed, cancelled. Enforce legal transitions, authorize cancellations and resumes, bind approvals to the exact immutable action, and cap iterations, retries, elapsed time, concurrency and tokens. Never describe retries as guaranteeing exactly-once external execution; use idempotency keys and reconciliation.

## Daily roadmap

Every row names work and evidence for that day. Detailed implementation is released one day at a time.

### Week 1 — AI and LLM fundamentals

| Day | Learning and implementation | Completion evidence / demo |
|---|---|---|
| 1 | Distinguish LLM, tool and agent; create FastAPI health and validated task-preview routes. | Valid JSON accepted, invalid input rejected; nine API tests. |
| 2 | Python functions, dictionaries, imports, exceptions and virtual environments; separate schema and service modules. | Explain the request in Python; behavior preserved after refactor. |
| 3 | Prompt/messages, model inference and backend secrets; make the first real Responses API call through an adapter. | Authorized live summary plus a mock-based test; record actual model ID. |
| 4 | Tokens, context limits, hallucinations, latency and failure categories; capture usage and timeout errors. | Compare two prompts; show actual usage and a simulated provider failure. |
| 5 | Build JavaScript/Tailwind dark dashboard shell and task form; connect frontend to FastAPI with explicit local CORS. | Loading, empty, success and failure states; no browser API secret. |
| 6 | Deliver task-to-LLM-summary vertical slice; add deterministic tests and GitHub CI. | UI submits a task and displays a real summary; Week 1 report. |
| 7 | Optional review/rest: replay the demo and explain LLM vs agent. | List misunderstandings and blockers; no new feature. |

### Week 2 — Prompts, structured outputs and tool calling

| Day | Learning and implementation | Completion evidence / demo |
|---|---|---|
| 8 | Prompt roles, constraints and examples; version a task-classification prompt. | Run the same small labeled task set against both prompt versions. |
| 9 | JSON Schema/Pydantic and Structured Outputs; produce typed task classifications. | Required fields validated; refusals and incomplete responses handled. |
| 10 | Define a narrow deterministic tool and its argument schema. | Tool gives known results and rejects invalid arguments without an LLM. |
| 11 | Build the tool-calling cycle: request, validate, execute, return result. | Trace actual tool call IDs and tool results through one model turn. |
| 12 | Add a tool registry, allowlists, output limits, timeouts and iteration caps. | Unknown/disallowed tool and excessive-call cases stop safely. |
| 13 | Build a bounded task planner that proposes subtasks and acceptance criteria. | Valid plan displayed; invalid plans rejected; Week 2 report. |
| 14 | Optional review/rest: reproduce one tool call from its trace. | Explain why a tool request alone cannot perform an action. |

### Week 3 — Single agent, memory and RAG

| Day | Learning and implementation | Completion evidence / demo |
|---|---|---|
| 15 | Introduce the Research Agent with a bounded observe/act loop and allowlisted retrieval. | Answer a narrow docs question using actual sources and a stopping condition. |
| 16 | Add local Docker PostgreSQL, SQLAlchemy models and Alembic migrations. | Save/reload a task, run and event; migration tested on an empty database. |
| 17 | Implement task execution history and short-term conversation/run memory. | Inspect two isolated runs; do not leak one run's context into the other. |
| 18 | Ingest authorized text/Markdown documents; scope by development workspace; chunk with source metadata. | Inspect saved chunks and provenance; size/type limits enforced. |
| 19 | Create embeddings and pgvector retrieval; introduce scoped long-term memory records. | Known query returns expected source; workspace filter and deletion checked. |
| 20 | Add grounded Research answers with citations, no-evidence fallback and history UI. | Supported answer and unsupported-question abstention; Week 3 report. |
| 21 | Optional review/rest: diagnose a retrieval miss. | Separate bad retrieval from bad answer generation. |

### Week 4 — LangGraph and orchestration

| Day | Learning and implementation | Completion evidence / demo |
|---|---|---|
| 22 | Learn state, nodes and edges; wrap existing research steps in a small StateGraph. | Visualize and execute the graph; no feature regression. |
| 23 | Add conditional routes and bounded error/stop paths. | Deterministic tests hit success, missing evidence and failure branches. |
| 24 | Add PostgreSQL-backed graph checkpoints with stable thread/run identity. | Restart process and resume a supported paused execution. |
| 25 | Separate API from worker using a PostgreSQL job queue with claim leases and heartbeat. | API returns a run ID quickly; two workers do not claim one active lease. |
| 26 | Stream execution events using SSE with ownership checks designed in; reconnect/poll fallback. | Timeline reconnects without duplicating events; cancellation recorded. |
| 27 | Introduce Manager Agent: create and validate plans; initially delegate only to Research. | Manager routes a supported task and rejects unsupported scope; Week 4 report. |
| 28 | Optional review/rest: explain persisted graph state vs queued jobs. | Kill a local worker and describe recovery evidence. |

### Week 5 — Multi-agent architecture and communication

| Day | Learning and implementation | Completion evidence / demo |
|---|---|---|
| 29 | Define specialist input/output contracts, typed messages and artifact ownership. | Invalid specialist output cannot enter the next step. |
| 30 | Add Developer Agent producing a small React component/patch artifact in an isolated workspace. | Artifact has requirements and references; it is not automatically executed. |
| 31 | Add QA Agent with test specifications and a controlled runner for trusted fixtures. | Distinguish model code review from actual runner output; failures preserved. |
| 32 | Add Documentation Agent producing README/change notes from verified artifacts and results. | Docs state actual test results and known limits. |
| 33 | Add Data Analysis Agent using deterministic CSV validation and calculation tools. | Known synthetic dataset yields exact expected totals; model explains results. |
| 34 | Connect all roles through Manager; add bounded parallelism only for independent work. | Research→Developer→QA→Docs trace and a separate CSV workflow; Week 5 report. |
| 35 | Optional review/rest: compare one-agent and multi-agent results. | Explain when another agent adds cost without improving quality. |

### Week 6 — Human approval, automation and errors

| Day | Learning and implementation | Completion evidence / demo |
|---|---|---|
| 36 | Define side-effect policy and add LangGraph approval interrupts with a persistent checkpointer. | Workflow pauses before an action; unrelated nodes continue only if permitted. |
| 37 | Build approve/reject UI and backend action binding, expiry and single-use resume. | Reject, expire, tamper and double-submit cases covered. |
| 38 | Add retries with jitter, deadlines, idempotency and failure categories. | Inject rate-limit and tool errors; no duplicate artifact on retry. |
| 39 | Add authorized automation schedules, cancellation, concurrency caps and stale-job recovery. | A local scheduled run records its trigger and can be cancelled. |
| 40 | Integrate a dedicated restricted code sandbox; enforce resource/network limits and human policy. | Approved generated fixture runs; runaway process times out; secret access denied. |
| 41 | Run crash/restart and duplicate-delivery scenarios across queue, graph and approval. | Recovery report with actual evidence and unresolved cases; Week 6 report. |
| 42 | Optional review/rest: recover one deliberately broken run. | Explain what is safe to retry and what needs reconciliation. |

### Week 7 — Production architecture, evaluation and security

| Day | Learning and implementation | Completion evidence / demo |
|---|---|---|
| 43 | Integrate established OIDC login and backend token validation; replace development identity. | Anonymous/invalid token rejected; login and logout work. |
| 44 | Enforce workspace membership, roles and ownership across every data/tool surface. | Cross-user run, SSE, artifact, retrieval, memory and approval access denied. |
| 45 | Add prompt-injection tests, URL/SSRF policy, upload limits and log redaction. | Malicious document cannot authorize tool execution or access internal URLs. |
| 46 | Build a versioned evaluation set; measure task success, citation support and tool correctness. | Compare baseline with current system; preserve failing examples. |
| 47 | Add per-model token ledger, dated price configuration, estimated costs and hard run limits. | Usage reconciles with recorded calls; budget exhaustion stops further calls. |
| 48 | Add metrics/tracing, load checks, dependency/secret scans, CI integration and performance fixes. | Measured latency/cost report and passing security regression checks; Week 7 report. |
| 49 | Optional review/rest: inspect evaluation failures and security findings. | Select only evidence-backed fixes for deployment week. |

### Week 8 — Deployment, docs and presentation

| Day | Learning and implementation | Completion evidence / demo |
|---|---|---|
| 50 | Package web/API/worker/database with Docker Compose, health checks and configuration docs. | Another local checkout starts using documented commands. |
| 51 | Deploy a restricted staging environment with managed PostgreSQL, worker and artifact storage. | Authenticated end-to-end run across actual deployed services. |
| 52 | Add readiness/liveness, migrations, backup and restore rehearsal; rollback procedure. | Restore sample data and roll back a staging app change. |
| 53 | Run live-model evaluation and complete UI/API end-to-end acceptance scenarios. | Separate deterministic tests, live evaluations and environment limitations. |
| 54 | Complete README, architecture decisions, OpenAPI guide, operational runbook and weekly-report index. | A colleague follows setup/demo instructions without private knowledge. |
| 55 | Polish dashboard accessibility/responsiveness; record final demo and limitations. | Accessible keyboard flow, error states and a rehearsed walkthrough; Week 8 report. |
| 56 | Optional review/rest: independent architecture explanation and mock interview. | Explain tradeoffs without reading generated notes. |

### Four final buffer days

| Day | Task | Evidence |
|---|---|---|
| 57 | Fix the highest-priority verified blocker or catch up on a missed session. | Reproduction and regression check; avoid speculative features. |
| 58 | Rehearse recovery, budget exhaustion and approval rejection on staging. | Final operational checklist with real outputs. |
| 59 | Deliver company presentation and final progress report. | Demo recording/instructions, feature matrix, measurements and limitations. |
| 60 | Complete an independent change: add a small specialist/tool, tests and docs. | Explain design, implement, test and deploy a reviewed change independently. |

## Specialist delivery sequence

Research Day 15 → Manager Day 27 → Developer Day 30 → QA Day 31 → Documentation Day 32 → Data Analysis Day 33. Day 13's planner is a bounded model call, not a complete Manager Agent. QA starts with trusted fixtures; generated-code execution waits for Day 40's sandbox and approval gate.

## Weekly report template

Week / commit / environment:
- Completed features and their acceptance evidence:
- Screenshot or reproducible demo steps:
- Actual deterministic test results:
- Actual live-model evaluation results (or not run):
- Technical challenges, root causes and fixes:
- Token usage / estimated costs / latency:
- Known limitations and blockers:
- Concepts I can explain independently:
- Next week's objectives:

Produce a report on Days 6, 13, 20, 27, 34, 41, 48 and 55. Preserve truthful failing results. Screenshots must come from the real app, not generated mockups.

## Final acceptance gates

1. Authenticated user submits a task and observes a durable run timeline.
2. Manager delegates only supported subtasks with bounded dependencies and tool permissions.
3. All six roles have an exercised workflow; not every task needs every role.
4. Grounded answers include usable sources and unsupported claims trigger fallback.
5. Developer artifacts and QA runner evidence are separate and traceable.
6. CSV calculations match known fixtures and uploaded data is scoped.
7. Approval rejection prevents the action; approval cannot be reused for a changed action.
8. Worker crash/restart and repeated delivery do not duplicate committed internal effects; external effects use reconciliation where needed.
9. Cross-user access and prompt-injection/SSRF/unsafe-tool attempts are tested and denied.
10. Usage, estimated costs, retries, failures and cancelled runs are visible.
11. Fresh setup, deployment, rollback and database restore are demonstrated.
12. Deterministic CI tests and a recorded live-model evaluation suite have separate results and documented limitations.

## Official documentation reference map

Verify feature/version compatibility again on the day it is implemented.
- Python functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
- Python environments: https://docs.python.org/3/tutorial/venv.html
- FastAPI first steps: https://fastapi.tiangolo.com/tutorial/first-steps/
- FastAPI request bodies: https://fastapi.tiangolo.com/tutorial/body/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- Starlette current TestClient dependencies: https://starlette.dev/testclient/
- OpenAI quickstart: https://developers.openai.com/api/docs/quickstart
- OpenAI function calling: https://developers.openai.com/api/docs/guides/function-calling
- OpenAI Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- Next.js installation: https://nextjs.org/docs/app/getting-started/installation
- SQLAlchemy tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
- Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- pgvector: https://github.com/pgvector/pgvector
- PostgreSQL: https://www.postgresql.org/docs/current/
