# Day 1 verification

Verified on 12 November 2026 in the mentor's execution environment.

- Python 3.12.14.
- Created a fresh virtual environment and installed backend/requirements.txt successfully.
- `python -m pip check`: No broken requirements found.
- `python -m unittest discover -s tests -v`: Ran 9 tests; OK.
- Real Uvicorn process on localhost: health 200; valid task preview 200; invalid input 422; OpenAPI contains task-preview route; docs route 200.
- No OpenAI calls, database, frontend, deployed services or browser-rendering checks were performed. They are outside Day 1.
- The learner's Ubuntu installation has not been tested; rerun the documented commands there.

The nine API checks cover health; valid response and UUID; whitespace trimming; rejection of blank, short, oversized, missing and non-string descriptions; and unknown-field rejection.

During the initial run, the installed Starlette reported that plain httpx for TestClient is deprecated. Official Starlette documentation confirmed httpx2 support. The supplied requirements use httpx2; fresh-environment tests passed without that warning.

backend/requirements.lock.txt records the transitive dependency versions from that successful installation. Use it for reproduction; update dependencies deliberately and retest.
