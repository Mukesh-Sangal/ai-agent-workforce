"use client";

import { useState } from "react";
import { analyzeTask } from "@/lib/api";

const EXAMPLE =
  "Build a React contact form with name and email fields only. " +
  "Submit to an existing API; the endpoint URL is not provided.";

export default function Home() {
  const [description, setDescription] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateDescription(value) {
    setDescription(value);
    setAnalysis(null);
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (loading) return;

    const task = description.trim();

    setError("");
    setAnalysis(null);

    if (task.length < 10 || task.length > 2000) {
      setError(
        "Enter a task description between 10 and 2,000 characters."
      );
      return;
    }

    setLoading(true);

    try {
      const result = await analyzeTask(task);
      setAnalysis(result);
    } catch (requestError) {
      setError(
        requestError.message ||
          "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen px-5 py-8 sm:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="flex items-center gap-3 border-b border-slate-800 pb-6">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-400 font-bold text-slate-950">
            AW
          </span>

          <div>
            <p className="font-semibold text-white">
              AI Agent Workforce
            </p>
            <p className="text-sm text-slate-400">
              Task analysis workspace
            </p>
          </div>
        </header>

        <section className="py-10">
          <p className="text-xs font-semibold uppercase tracking-widest text-emerald-400">
            Start with a clear brief
          </p>

          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            What would you like to work on?
          </h1>

          <p className="mt-3 max-w-2xl leading-7 text-slate-400">
            Describe your task to identify its goal, expected
            deliverable and details that need clarification.
          </p>
        </section>

        <div className="grid items-start gap-6 lg:grid-cols-2">
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div className="mb-6 flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-white">
                Describe your task
              </h2>

              <button
                type="button"
                disabled={loading}
                onClick={() => updateDescription(EXAMPLE)}
                className="rounded text-sm text-emerald-400 hover:text-emerald-300 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald-400 disabled:opacity-50"
              >
                Use example
              </button>
            </div>

            <form
              onSubmit={handleSubmit}
              noValidate
              aria-busy={loading}
            >
              <label
                htmlFor="description"
                className="mb-2 block text-sm font-medium"
              >
                Task description
              </label>

              <textarea
                id="description"
                value={description}
                onChange={(event) =>
                  updateDescription(event.target.value)
                }
                disabled={loading}
                required
                maxLength={2000}
                rows={8}
                aria-describedby={
                  error ? "task-help task-error" : "task-help"
                }
                placeholder="For example: Build an accessible React contact form..."
                className="w-full resize-y rounded-xl border border-slate-700 bg-slate-950 p-4 text-sm leading-6 text-slate-100 placeholder:text-slate-500 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/20 disabled:opacity-60"
              />

              <div
                id="task-help"
                className="mt-2 flex justify-between gap-4 text-xs text-slate-400"
              >
                <span>10–2,000 characters</span>
                <span>{description.length}/2,000</span>
              </div>

              {error && (
                <p
                  id="task-error"
                  role="alert"
                  className="mt-4 rounded-lg border border-rose-400/30 bg-rose-400/10 p-3 text-sm text-rose-200"
                >
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="mt-6 w-full rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-emerald-300 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-emerald-400 disabled:cursor-wait disabled:opacity-60"
              >
                {loading ? "Analyzing task…" : "Analyze task"}
              </button>
            </form>

            <p className="mt-4 text-xs leading-5 text-slate-400">
              Analysis helps define the work. Review the result
              before planning or execution.
            </p>
          </section>

          <section
            aria-live="polite"
            aria-busy={loading}
            className="min-h-96 rounded-2xl border border-slate-800 bg-slate-900 p-6"
          >
            <h2 className="text-lg font-semibold text-white">
              Task brief
            </h2>

            {loading ? (
              <div
                role="status"
                className="mt-8 space-y-4 text-sm text-slate-400"
              >
                <p>Reading your requirements…</p>

                {[1, 2, 3].map((item) => (
                  <div
                    key={item}
                    className="h-12 rounded-lg bg-slate-800 motion-safe:animate-pulse"
                  />
                ))}
              </div>
            ) : analysis ? (
              <div className="mt-6 space-y-6">
                {[
                  ["Goal", analysis.goal],
                  [
                    "Expected deliverable",
                    analysis.expected_deliverable,
                  ],
                ].map(([title, text]) => (
                  <div key={title}>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                      {title}
                    </h3>

                    <p className="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-slate-200">
                      {text}
                    </p>
                  </div>
                ))}

                <div className="border-t border-slate-800 pt-5">
                  <h3 className="text-sm font-semibold text-white">
                    Clarification questions
                  </h3>

                  {analysis.missing_information.length > 0 ? (
                    <ul className="mt-3 list-disc space-y-3 pl-5 text-sm leading-6 text-slate-300">
                      {analysis.missing_information.map(
                        (question, index) => (
                          <li key={`${index}-${question}`}>
                            {question}
                          </li>
                        )
                      )}
                    </ul>
                  ) : (
                    <p className="mt-3 text-sm text-slate-400">
                      No clarification questions were returned.
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="grid min-h-72 content-center text-center">
                <p className="text-lg font-medium text-slate-200">
                  Your task brief will appear here
                </p>

                <p className="mx-auto mt-3 max-w-xs text-sm leading-6 text-slate-400">
                  Add a description and select Analyze task to
                  get started.
                </p>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}