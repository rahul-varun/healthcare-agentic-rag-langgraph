"use client";

import { useState } from "react";
import { ApiError, GraphQueryResponse, queryGraph } from "../lib/api";

export default function GraphExplorerPage() {
  const [entity, setEntity] = useState("");
  const [otherEntity, setOtherEntity] = useState("");
  const [response, setResponse] = useState<GraphQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!entity.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const result = await queryGraph(entity, otherEntity || undefined);
      setResponse(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Request failed — is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl p-8">
      <p className="eyebrow">Coverage map</p>
      <h1 className="mt-2 text-3xl font-semibold text-white">Explore your care network</h1>
      <p className="mt-1 text-sm text-neutral-400">
        See how a health plan connects benefits, treatments, hospitals, documents, and eligibility rules.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 flex flex-wrap gap-2">
        <input
          value={entity}
          onChange={(e) => setEntity(e.target.value)}
          placeholder="Entity (e.g. maternity benefit)"
          className="flex-1 rounded-md border border-neutral-700 bg-neutral-950 px-4 py-2 text-sm text-neutral-100 placeholder:text-neutral-500 focus:border-neutral-500 focus:outline-none"
        />
        <input
          value={otherEntity}
          onChange={(e) => setOtherEntity(e.target.value)}
          placeholder="Other entity (optional, for path between)"
          className="flex-1 rounded-md border border-neutral-700 bg-neutral-950 px-4 py-2 text-sm text-neutral-100 placeholder:text-neutral-500 focus:border-neutral-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-neutral-100 px-5 py-2 text-sm font-medium text-neutral-900 disabled:opacity-50"
        >
          {loading ? "Querying…" : "Query"}
        </button>
      </form>

      {error && (
        <div className="mt-4 rounded-md border border-red-900 bg-red-950/50 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {response && (
        <div className="mt-6 rounded-md border border-neutral-800 bg-neutral-950 p-4">
          {response.results.length === 0 ? (
            <p className="text-sm text-neutral-500">No relationships found for this entity.</p>
          ) : (
            <ul className="space-y-2 text-sm text-neutral-200">
              {response.results.map((result, i) => (
                <li key={i} className="border-b border-neutral-900 pb-2 last:border-0">
                  <pre className="whitespace-pre-wrap font-mono text-xs text-neutral-400">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
