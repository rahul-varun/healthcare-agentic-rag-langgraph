"use client";

import { useState } from "react";
import { ApiError, EvaluationResponse, runEvaluation } from "../lib/api";

const METRIC_LABELS: Record<string, string> = {
  hit_rate: "Hit Rate",
  reciprocal_rank: "MRR",
  recall_at_k: "Recall@k",
  ndcg_at_k: "NDCG@k",
};

export default function EvaluationPage() {
  const [result, setResult] = useState<EvaluationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setLoading(true);
    setError(null);
    try {
      const res = await runEvaluation();
      setResult(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Evaluation run failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl p-8">
      <h1 className="text-xl font-semibold text-neutral-50">Evaluation</h1>
      <p className="mt-1 text-sm text-neutral-400">
        Runs the retrieval smoke dataset against the live hybrid + reranked retriever. Small sample size — useful to
        confirm the pipeline works, not a statistically meaningful benchmark.
      </p>

      <button
        onClick={handleRun}
        disabled={loading}
        className="mt-6 rounded-md bg-neutral-100 px-5 py-2 text-sm font-medium text-neutral-900 disabled:opacity-50"
      >
        {loading ? "Running…" : "Run evaluation"}
      </button>

      {error && (
        <div className="mt-4 rounded-md border border-red-900 bg-red-950/50 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {Object.entries(result.aggregate).map(([key, value]) => (
              <div key={key} className="rounded-md border border-neutral-800 bg-neutral-950 p-4">
                <p className="text-xs text-neutral-500">{METRIC_LABELS[key] || key}</p>
                <p className="mt-1 text-lg font-semibold text-neutral-100">{value.toFixed(2)}</p>
              </div>
            ))}
          </div>

          <div>
            <h2 className="mb-2 text-sm font-medium text-neutral-400">
              Per-question results ({result.n_questions} questions)
            </h2>
            <table className="w-full border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-neutral-800 text-neutral-400">
                  <th className="py-2 pr-4 font-medium">Question</th>
                  <th className="py-2 pr-2 font-medium">Hit</th>
                  <th className="py-2 pr-2 font-medium">MRR</th>
                  <th className="py-2 font-medium">NDCG</th>
                </tr>
              </thead>
              <tbody>
                {result.per_question.map((q, i) => (
                  <tr key={i} className="border-b border-neutral-900 text-neutral-200">
                    <td className="py-2 pr-4">{q.question}</td>
                    <td className="py-2 pr-2">{q.hit_rate.toFixed(2)}</td>
                    <td className="py-2 pr-2">{q.reciprocal_rank.toFixed(2)}</td>
                    <td className="py-2">{q.ndcg_at_k.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
