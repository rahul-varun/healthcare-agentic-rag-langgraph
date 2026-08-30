const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // response body wasn't JSON — fall back to statusText
    }
    throw new ApiError(response.status, detail);
  }
  return response.json() as Promise<T>;
}

export interface TraceSpan {
  node: string;
  duration_ms: number;
}

export interface ChatResponse {
  answer: string;
  sources: Record<string, unknown>[];
  intent: string | null;
  tool_calls: string[];
  errors: string[];
  output_policy: string | null;
  trace: TraceSpan[];
}

export type ResponseLanguage = "english" | "hindi" | "hinglish" | "tamil";

export function sendChat(query: string, topK = 5, responseLanguage: ResponseLanguage = "english"): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ query, top_k: topK, response_language: responseLanguage }),
  });
}

export interface GraphQueryResponse {
  results: Record<string, unknown>[];
}

export function queryGraph(entity: string, otherEntity?: string, maxHops = 2): Promise<GraphQueryResponse> {
  return request<GraphQueryResponse>("/api/graph/query", {
    method: "POST",
    body: JSON.stringify({ entity, other_entity: otherEntity || null, max_hops: maxHops }),
  });
}

export interface EvaluationQuestionResult {
  question: string;
  hit_rate: number;
  reciprocal_rank: number;
  recall_at_k: number;
  ndcg_at_k: number;
}

export interface EvaluationResponse {
  aggregate: Record<string, number>;
  per_question: EvaluationQuestionResult[];
  n_questions: number;
}

export function runEvaluation(): Promise<EvaluationResponse> {
  return request<EvaluationResponse>("/api/evaluation/run", { method: "POST" });
}

export interface DocumentInfo {
  name: string;
  type: string;
  size_bytes: number;
  relative_path: string;
}

export function listDocuments(): Promise<{ documents: DocumentInfo[] }> {
  return request("/api/documents");
}

export async function uploadDocument(file: File): Promise<{ name: string; type: string; chunks: number; status: string }> {
  const form = new FormData();
  form.append("file", file);
  const headers: Record<string, string> = {};
  if (API_KEY) headers["X-API-Key"] = API_KEY;
  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, { method: "POST", headers, body: form });
  if (!response.ok) {
    let detail = response.statusText;
    try { detail = (await response.json()).detail || detail; } catch { /* non-JSON response */ }
    throw new ApiError(response.status, detail);
  }
  return response.json();
}

export interface MetricsResponse {
  request_count: number;
  error_count: number;
  total_input_tokens: number;
  total_output_tokens: number;
  tool_call_counts: Record<string, number>;
  estimated_cost_usd: number;
}

export function getMetrics(): Promise<MetricsResponse> {
  return request("/api/metrics");
}

export interface ReadinessResponse {
  vector_store: string;
  neo4j: string;
  postgres: string;
}

export function getReadiness(): Promise<ReadinessResponse> {
  return request("/api/health/ready");
}
