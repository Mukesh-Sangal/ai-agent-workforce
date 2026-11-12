# Day 1 — Understand an agent and build its task-intake boundary

## 1. Learning objective

Explain how an LLM differs from a tool and an agent, then run a small Python API that accepts and validates a task. Success means you can explain the request path, demonstrate accepted/rejected inputs and run the nine provided tests yourself.

## 2. What to understand today

An LLM generates outputs from provided context. It can produce useful text or request a tool call, but those outputs can be wrong.

A tool is application code with a defined input and output. A model can request that a tool be called; the backend validates and executes it under explicit permissions.

An agent combines a model, instructions, tools and state with a bounded control loop: receive goal, select a step, execute an allowed tool, observe its result, decide whether to continue and stop. A workflow can instead follow predetermined steps. We will use deterministic workflow rules around model decisions.

A role name such as Research Agent does not make a system autonomous. Observable behavior, tools, stopping rules and evidence matter.

Today the only implementation is a deterministic API boundary. A preview does not mean that a job was saved, scheduled or completed. The first real model call is planned for Day 3.

## 3. Why this matters

Every future Manager request passes through a backend boundary. Rejecting invalid inputs here makes later model calls easier to test and prevents avoidable calls on unusable requests. This is input validation, not complete prompt-injection protection or semantic task validation.

## 4. Official reading — about 40 minutes

Read only the relevant sections today:
- Python defining functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
- FastAPI first steps: https://fastapi.tiangolo.com/tutorial/first-steps/
- FastAPI request bodies: https://fastapi.tiangolo.com/tutorial/body/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- Current Starlette TestClient dependency note: https://starlette.dev/testclient/

Bookmark for later, without implementing today:
- OpenAI quickstart: https://developers.openai.com/api/docs/quickstart
- OpenAI tool calling: https://developers.openai.com/api/docs/guides/function-calling

## 5. Six-hour schedule and implementation

| Hour | Activity | Evidence |
|---|---|---|
| 1 | Learn LLM/tool/agent/workflow distinctions; read the listed sections. | Explain each using the contact-form task. |
| 2 | Practice Python functions, strings and return; set up the virtual environment. | Translate and run the small exercise below. |
| 3 | Create the API and request/response models. | Explain each block before proceeding. |
| 4 | Add validation, ID logging, tests and environment/Git hygiene. | Run a valid and invalid request. |
| 5 | Run automated checks and fix local setup issues. | Save your actual test output. |
| 6 | Write notes, commit and rehearse the company demo. | Commit plus a two-minute walkthrough. |

Exercise: compare JavaScript and Python.

```javascript
function cleanDescription(value) {
  return value.trim();
}
console.log(cleanDescription("  Review contact form  "));
```

```python
def clean_description(value: str) -> str:
    return value.strip()

print(clean_description("  Review contact form  "))
```

`def` declares a Python function; indentation defines its body. `str` means string. `-> str` documents the return type; ordinary Python does not enforce annotations automatically. `.strip()` removes surrounding whitespace. Pydantic, used below, does perform runtime validation.

Extract the starter, or create the paths in the README and paste each file below. From the project root:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.lock.txt
cd backend
```

The verified baseline is Python 3.12.14. The full lockfile is included in this package. If copying only the inline files, install `backend/requirements.txt` instead. A virtual environment isolates this project's packages from your system Python. Do not use sudo pip.

## 6. Complete Day 1 source

Create backend/app/__init__.py as an empty file. The remaining files follow.

### backend/requirements.txt

```text
fastapi==0.141.1
pydantic==2.13.4
uvicorn==0.52.1
starlette==1.6.0
httpx2==2.16.0
```

### backend/app/main.py

```python
import logging
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("workforce")

app = FastAPI(title="AI Agent Workforce", version="0.1.0")


class TaskRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True, extra="forbid", strict=True
    )
    description: str = Field(min_length=10, max_length=2000)


class TaskPreview(BaseModel):
    id: UUID
    description: str
    status: Literal["preview_only"] = "preview_only"
    model_called: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/task-previews", response_model=TaskPreview)
def preview_task(task: TaskRequest) -> TaskPreview:
    preview = TaskPreview(id=uuid4(), description=task.description)
    logger.info("task_preview_created id=%s", preview.id)
    return preview
```

### backend/tests/test_api.py

```python
import unittest
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_valid_preview(self):
        description = "Research accessible contact form patterns."
        response = self.client.post(
            "/task-previews", json={"description": description}
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        UUID(body["id"])
        self.assertEqual(body["description"], description)
        self.assertEqual(body["status"], "preview_only")
        self.assertIs(body["model_called"], False)

    def test_trims_whitespace(self):
        response = self.client.post(
            "/task-previews", json={"description": "  Review this contact form.  "}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["description"], "Review this contact form.")

    def test_rejects_blank_description(self):
        response = self.client.post("/task-previews", json={"description": " " * 20})
        self.assertEqual(response.status_code, 422)

    def test_rejects_short_description(self):
        response = self.client.post("/task-previews", json={"description": "short"})
        self.assertEqual(response.status_code, 422)

    def test_rejects_oversized_description(self):
        response = self.client.post("/task-previews", json={"description": "a" * 2001})
        self.assertEqual(response.status_code, 422)

    def test_rejects_missing_description(self):
        response = self.client.post("/task-previews", json={})
        self.assertEqual(response.status_code, 422)

    def test_rejects_unknown_fields(self):
        response = self.client.post(
            "/task-previews", json={"description": "Review this contact form.", "admin": True}
        )
        self.assertEqual(response.status_code, 422)

    def test_rejects_non_string_description(self):
        response = self.client.post("/task-previews", json={"description": 1234567890})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
```

### .gitignore

```gitignore
.venv/
__pycache__/
*.py[cod]
.env
.env.*
!.env.example
node_modules/
.next/
coverage/
*.log
```

### .env.example

```dotenv
# Reserved for Day 3. Day 1 does not load this file or call OpenAI.
# Keep real values in a backend-only .env file excluded by Git.
OPENAI_API_KEY=
OPENAI_MODEL=
```

## 7. Important code explanations

- `FastAPI(...)` constructs the application. `@app.get` and `@app.post` register routes. The decorator connects a URL/method to the function below it.
- `TaskRequest(BaseModel)` defines an input schema. It inherits validation behavior from Pydantic; it is more than a plain Python dictionary.
- `description: str` declares a string field. `Field` requires 10–2000 characters after trimming. `strict=True` rejects an integer rather than converting it; `extra="forbid"` rejects unknown fields.
- FastAPI reads the JSON body into `TaskRequest` before the endpoint runs. Failed validation returns HTTP 422. This is expected application behavior, not a server crash.
- `TaskPreview` defines the response. `Literal["preview_only"]` permits one status value. The model-called flag truthfully reports false for this endpoint.
- `uuid4()` supplies an identifier. It is not a database save. Repeated previews have new IDs and no execution history.
- `response_model=TaskPreview` defines and validates the response contract and helps generate the API documentation.
- The logger records an event name and preview ID, not the submitted description or API keys.
- Normal `def` is sufficient for these short synchronous handlers. We will explain `async def` and `await` before adding asynchronous network operations.
- Tests use Python's built-in unittest with FastAPI's TestClient. No pytest installation is needed today. TestClient exercises the app in-process; a real-server smoke test was also performed, as recorded separately.
- Standard request-validation errors are handled by FastAPI. We do not add broad exception handlers that hide programming errors or return HTTP 200 for failures.

The current Starlette docs recommend httpx2 for TestClient. The pinned dependencies were installed and verified in a clean virtual environment. The plain httpx version found in some older examples is not required by this starter.

## 8. Run the application

From the backend directory with the virtual environment activated:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Keep this terminal open. Open http://127.0.0.1:8000/docs in a browser.

Expand POST /task-previews → Try it out → submit:

```json
{"description":"Research accessible contact form patterns."}
```

A successful response has status 200, your description, status `preview_only`, model_called false and a generated UUID. The UUID changes on each request. No model reasoning, storage or background execution takes place.

From a second terminal:

```bash
curl -i http://127.0.0.1:8000/health
curl -i -X POST http://127.0.0.1:8000/task-previews \
  -H 'Content-Type: application/json' \
  -d '{"description":"Research accessible contact form patterns."}'
curl -i -X POST http://127.0.0.1:8000/task-previews \
  -H 'Content-Type: application/json' \
  -d '{"description":" "}'
```

The first two requests should return 200. The last should return 422. These are expectations to verify on your machine, not a claim that you have already run them.

## 9. Test and debug

From backend in a second activated terminal:

```bash
python -m unittest discover -s tests -v
python -m pip check
```

Actually verified in the supplied execution environment: clean installation; nine tests passed; pip check passed; real Uvicorn HTTP health/valid/invalid/OpenAPI/docs-route checks passed. A browser-rendering check and live OpenAI call were not performed. See TEST_RESULTS.md.

| Symptom | Check or action |
|---|---|
| `No module named app` | Run the server/test commands from backend. |
| `No module named fastapi` | Activate .venv and run `python -m pip --version`; install the requirements into that interpreter. |
| venv/ensurepip unavailable on Ubuntu | Install your Python version's venv package through apt, then recreate the environment. For default Ubuntu Python, this is commonly `sudo apt install python3-venv`. |
| Port 8000 already in use | Use `--port 8001` and update the browser/curl URL. |
| HTTP 422 for valid-looking input | Inspect the response detail: field name, type, trimmed length or unknown field. |
| Connection refused | Confirm the server terminal is still running and the port matches. |
| Browser request to `/` returns 404 | Expected: today we define /health, /task-previews and automatic docs, not a homepage. |
| Dependency installation fails | Preserve the exact error and Python version; do not randomly upgrade all packages. |

Break the health response temporarily and observe the health test fail; then restore the code and rerun. This proves your local tests can detect a regression. Do not commit the deliberate failure.

## 10. Connection to the main project

Today: validated task preview. Later: the task service will persist the task and create a durable run; Manager will receive the validated description; specialist results will be stored as artifacts; the dashboard will display actual execution events and evidence. We deliberately name today's endpoint preview to avoid implying work is queued.

## 11. Git commit

From the extracted project root, initialize a local repository if this is a new project:

```bash
git init
git add .gitignore .env.example README.md backend docs
git diff --cached --stat
git commit -m "feat: add validated task preview API and day-one tests"
```

Inspect `git status` and ensure no real .env file or key is staged. If Git asks for identity, configure your name/email before committing. No remote GitHub repository or push is performed by these commands.

## 12. End-of-day summary to write in your own words

Use docs/DAILY_PROGRESS_TEMPLATE.md. Record that you learned the distinction between a model, a tool and an agent; built a FastAPI boundary; used Pydantic to validate a request; checked accepted and rejected input; and ran tests. Write your actual local results and any remaining blockers. State that no AI execution has been added yet.

## 13. Questions before Day 2

1. Why is today's API not yet an AI agent?
2. What executes a tool: the LLM or your backend? What checks belong before execution?
3. Why does an all-spaces description fail after trimming?
4. What is the difference between a Python type annotation and Pydantic validation?
5. Why does a generated UUID not prove that a task was saved?
6. What does HTTP 422 tell the frontend?
7. Where should the OpenAI key live when we add it, and why?

Also answer the starting-assessment questions in ROADMAP.md. Say “new to me” where appropriate. Your explanations and local test output determine how much Python practice Day 2 needs.

## 14. Company demonstration — about two minutes

Show the actual running application rather than a slide of planned features:

1. Show /health returning ok.
2. Submit the contact-form research task through /docs; point out its UUID, preview status and model_called false.
3. Submit a blank task and show HTTP 422.
4. Run the nine tests and show your actual result.
5. Explain: “This is the input-validation foundation for our AI workforce. It catches unusable requests before they reach the Manager. Today it validates and previews tasks; the first model integration comes on Day 3. I learned how Python request schemas and API tests work. Next I will strengthen the Python modules and separate the service logic.”

Only say tests passed if they passed on your machine. We will review your answers and output before advancing to the next major concept.
