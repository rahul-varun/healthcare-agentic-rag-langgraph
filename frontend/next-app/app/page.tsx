"use client";

import { useState } from "react";
import { ApiError, ChatResponse, ResponseLanguage, sendChat } from "./lib/api";
import { formatSource, labelForNode } from "./lib/trace";
import MarkdownContent from "./components/MarkdownContent";

export default function ChatPage() {
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState<ResponseLanguage>("hinglish");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const quickPrompts = ["What are the red flags?", "Explain the treatment", "What medicines are mentioned?"];

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const result = await sendChat(query, 5, language);
      setResponse(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Request failed — is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-6xl flex-col gap-8 p-6 md:p-10">
      <header className="flex items-start justify-between gap-4">
        <div>
        <p className="eyebrow">HealthAgent AI</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">Your evidence-based health companion.</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Ask about symptoms, treatments, medicines, guidelines, and care decisions - grounded in your uploaded medical documents.</p>
        </div>
        <label className="flex items-center gap-2 text-right sm:block"><span className="hidden text-[10px] font-bold tracking-[.16em] text-slate-500 sm:block">RESPONSE LANGUAGE</span><select value={language} onChange={(e) => setLanguage(e.target.value as ResponseLanguage)} className="language-select" aria-label="Response language"><option value="english">English</option><option value="hindi">हिन्दी</option><option value="hinglish">Hinglish</option><option value="tamil">தமிழ் (Tamil)</option></select></label>
      </header>

      <div className="search-sticky">
        <form onSubmit={handleSubmit} className="question-card flex flex-col gap-3 sm:flex-row">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Is my hospital stay covered under this health card?"
            className="flex-1 rounded-md border border-neutral-700 bg-neutral-950 px-4 py-2 text-sm text-neutral-100 placeholder:text-neutral-500 focus:border-neutral-500 focus:outline-none"
          />
          <button type="submit" disabled={loading} className="button-primary disabled:opacity-50">
            {loading ? "Thinking…" : "Send"}
          </button>
        </form>
        <div className="mt-2 flex flex-wrap items-center gap-2"><span className="mr-1 text-[11px] text-slate-600">Try asking</span>{quickPrompts.map((prompt) => <button key={prompt} type="button" onClick={() => setQuery(prompt)} className="prompt-chip">{prompt}</button>)}</div>
      </div>

      {error && (
        <div className="rounded-md border border-red-900 bg-red-950/50 px-4 py-3 text-sm text-red-300">{error}</div>
      )}

      {response && (
        <div className="grid flex-1 grid-cols-1 gap-6 md:grid-cols-[2fr_1fr]">
          <section className="flex flex-col gap-4">
            <div className="answer-card p-6">
              <div className="mb-5 flex items-center justify-between border-b border-white/10 pb-4"><div className="flex items-center gap-3"><span className="answer-icon">✦</span><div><h2 className="text-sm font-semibold text-white">HealthAgent AI answer</h2><p className="mt-0.5 text-[11px] text-slate-500">Synthesized from your knowledge base</p></div></div>{response.output_policy && <span className="status-pill">{response.output_policy === "SAFE" ? "✓ Verified" : "Review needed"}</span>}</div>
              <MarkdownContent content={response.answer} />
              {response.output_policy && (
                <span
                  className={`mt-3 inline-block rounded px-2 py-0.5 text-xs font-medium ${
                    response.output_policy === "SAFE"
                      ? "bg-emerald-950 text-emerald-400"
                      : response.output_policy === "NEEDS_REVIEW"
                        ? "bg-amber-950 text-amber-400"
                        : "bg-red-950 text-red-400"
                  }`}
                >
                  {response.output_policy}
                </span>
              )}
            </div>

            {response.errors.length > 0 && (
              <div className="rounded-md border border-amber-900 bg-amber-950/40 p-4 text-xs text-amber-300">
                <h3 className="mb-1 font-medium">Tool notices</h3>
                <ul className="list-inside list-disc space-y-0.5">
                  {response.errors.map((err, i) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          <aside className="flex flex-col gap-4">
            <div className="surface p-5">
              <h2 className="mb-3 text-sm font-medium text-neutral-400">Agent activity</h2>
              {response.intent && (
                <p className="mb-2 text-xs text-neutral-500">
                  Intent: <span className="text-neutral-300">{response.intent}</span>
                </p>
              )}
              <ul className="space-y-1.5 text-sm text-neutral-300">
                {response.trace.map((span, i) => (
                  <li key={i} className="flex items-center justify-between gap-2">
                    <span>✓ {labelForNode(span.node)}</span>
                    <span className="text-xs text-neutral-500">{span.duration_ms}ms</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="surface p-5">
              <h2 className="mb-3 text-sm font-medium text-neutral-400">Sources</h2>
              {response.sources.length === 0 ? (
                <p className="text-sm text-neutral-500">No sources retrieved.</p>
              ) : (
                <ul className="space-y-2 text-sm text-neutral-300">
                  {response.sources.map((source, i) => (
                    <li key={i} className="border-b border-neutral-900 pb-2 last:border-0 last:pb-0">
                      {formatSource(source)}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}
