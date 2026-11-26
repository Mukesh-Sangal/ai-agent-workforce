import test from "node:test";
import assert from "node:assert/strict";

import { analyzeTask } from "../lib/api.js";

const DESCRIPTION = "Build a React contact form.";

const VALID_ANALYSIS = {
  goal: "Build a React contact form.",
  expected_deliverable: "A reusable React form component.",
  missing_information: [
    "What is the API endpoint URL?",
  ],
};

test("sends one POST request and returns the analysis", async (t) => {
  const fetchMock = t.mock.method(
    globalThis,
    "fetch",
    async () => Response.json(VALID_ANALYSIS)
  );

  const result = await analyzeTask(DESCRIPTION);

  assert.deepEqual(result, VALID_ANALYSIS);
  assert.equal(fetchMock.mock.callCount(), 1);

  const [url, options] = fetchMock.mock.calls[0].arguments;
  const parsedUrl = new URL(url);

  assert.ok(["http:", "https:"].includes(parsedUrl.protocol));
  assert.equal(parsedUrl.pathname, "/task-analyses");
  assert.equal(options.method, "POST");
  assert.equal(options.headers["Content-Type"], "application/json");

  assert.deepEqual(JSON.parse(options.body), {
    description: DESCRIPTION,
  });
});

test("accepts an empty clarification list", async (t) => {
  const analysis = {
    ...VALID_ANALYSIS,
    missing_information: [],
  };

  t.mock.method(
    globalThis,
    "fetch",
    async () => Response.json(analysis)
  );

  const result = await analyzeTask(DESCRIPTION);

  assert.deepEqual(result.missing_information, []);
});

test("rejects missing or incorrectly typed response fields", async (t) => {
  let responseBody;

  t.mock.method(
    globalThis,
    "fetch",
    async () => Response.json(responseBody)
  );

  const invalidResponses = [
    {
      ...VALID_ANALYSIS,
      goal: undefined,
    },
    {
      ...VALID_ANALYSIS,
      expected_deliverable: undefined,
      expected_deliverables: "Incorrect plural field name.",
    },
    {
      ...VALID_ANALYSIS,
      missing_information: undefined,
      missing_infomation: [],
    },
    {
      ...VALID_ANALYSIS,
      missing_information: "Unknown",
    },
    {
      ...VALID_ANALYSIS,
      missing_information: [123],
    },
  ];

  for (const invalidResponse of invalidResponses) {
    responseBody = invalidResponse;

    await assert.rejects(
      () => analyzeTask(DESCRIPTION),
      /unexpected analysis format/i
    );
  }
});

test("displays a backend error message", async (t) => {
  t.mock.method(
    globalThis,
    "fetch",
    async () =>
      Response.json(
        { detail: "Analysis service is temporarily unavailable." },
        { status: 503 }
      )
  );

  await assert.rejects(
    () => analyzeTask(DESCRIPTION),
    /Analysis service is temporarily unavailable/
  );
});

test("extracts messages from FastAPI validation errors", async (t) => {
  t.mock.method(
    globalThis,
    "fetch",
    async () =>
      Response.json(
        {
          detail: [
            {
              loc: ["body", "description"],
              msg: "String should have at least 10 characters",
              type: "string_too_short",
            },
          ],
        },
        { status: 422 }
      )
  );

  await assert.rejects(
    () => analyzeTask(DESCRIPTION),
    /String should have at least 10 characters/
  );
});

test("converts a network failure into a connection message", async (t) => {
  t.mock.method(globalThis, "fetch", async () => {
    throw new TypeError("Failed to fetch");
  });

  await assert.rejects(
    () => analyzeTask(DESCRIPTION),
    /Cannot reach the analysis service/
  );
});

test("converts AbortError into a timeout message", async (t) => {
  t.mock.method(globalThis, "fetch", async () => {
    throw new DOMException(
      "The operation was aborted.",
      "AbortError"
    );
  });

  await assert.rejects(
    () => analyzeTask(DESCRIPTION),
    /request timed out/i
  );
});