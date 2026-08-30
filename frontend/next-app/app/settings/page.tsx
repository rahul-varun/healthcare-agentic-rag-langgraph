"use client";

import { useEffect, useState } from "react";
import { ApiError, ReadinessResponse, getReadiness } from "../lib/api";

const ENV_VARS: { name: string; description: string }[] = [
  { name: "OPENROUTER_API_KEY", description: "LLM provider key (OpenRouter). Required for generation." },
  { name: "NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD", description: "Knowledge graph connection." },
  { name: "POSTGRES_URL", description: "Structured data connection for the SQL tool." },
  { name: "TAVILY_API_KEY", description: "Web search tool provider key." },
  { name: "API_KEY", description: "If set, required as X-API-Key on chat/graph/evaluation endpoints." },
  { name: "RATE_LIMIT_MAX_REQUESTS / RATE_LIMIT_WINDOW_SECONDS", description: "Per-client rate limiting." },
];

function StatusDot({ status }: { status: string }) {
  const color = status === "up" ? "bg-emerald-500" : "bg-red-500";
  return <span className={`inline-block h-2 w-2 rounded-full ${color}`} />;
}

export default function SettingsPage() {
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getReadiness()
      .then(setReadiness)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load system status"));
  }, []);

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="text-xl font-semibold text-neutral-50">Settings</h1>

      <section className="mt-6">
        <h2 className="mb-3 text-sm font-medium text-neutral-400">System status</h2>
        {error && <p className="text-sm text-red-400">{error}</p>}
        {readiness && (
          <ul className="space-y-2 text-sm text-neutral-200">
            {Object.entries(readiness).map(([component, status]) => (
              <li key={component} className="flex items-center gap-2">
                <StatusDot status={status} />
                <span className="capitalize">{component.replace("_", " ")}</span>
                <span className="text-neutral-500">— {status}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-sm font-medium text-neutral-400">Configuration (.env)</h2>
        <p className="mb-3 text-xs text-neutral-500">
          Values are never exposed here — configure them in the backend&apos;s .env file. See .env.example.
        </p>
        <ul className="divide-y divide-neutral-900 text-sm">
          {ENV_VARS.map((item) => (
            <li key={item.name} className="py-2">
              <p className="font-mono text-neutral-200">{item.name}</p>
              <p className="text-xs text-neutral-500">{item.description}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
