export const NODE_LABELS: Record<string, string> = {
  guardrail: "Input guardrail checked",
  classifier: "Query classified",
  rewriter: "Query rewritten",
  planner: "Plan created",
  retrieve: "Hybrid retrieval completed",
  graph_search: "Knowledge graph searched",
  sql: "SQL executed",
  web_search: "Web search executed",
  calculator: "Calculator used",
  clinical_info_agent: "Clinical information reviewed",
  medication_safety_agent: "Medication safety reviewed",
  web_evidence_agent: "Web evidence reviewed",
  generate: "Answer generated",
  evidence_check: "Evidence verified",
  output_guardrail: "Output guardrail applied",
};

export function labelForNode(node: string): string {
  return NODE_LABELS[node] || node;
}

export function formatSource(source: Record<string, unknown>): string {
  if (typeof source.document === "string") {
    const headingPath = Array.isArray(source.heading_path) ? source.heading_path.join(" > ") : null;
    return headingPath ? `${source.document} — ${headingPath}` : source.document;
  }
  if (typeof source.document_name === "string") {
    return typeof source.page === "number" ? `${source.document_name}, page ${source.page}` : source.document_name;
  }
  if (typeof source.expression === "string") {
    return `Calculator: ${source.expression} = ${source.result}`;
  }
  if (typeof source.url === "string") {
    return typeof source.title === "string" ? `${source.title} (${source.url})` : source.url;
  }
  if (typeof source.source === "string" && typeof source.target === "string") {
    return `${source.source} → ${source.target}`;
  }
  const entries = Object.entries(source).slice(0, 3);
  return entries.map(([key, value]) => `${key}: ${String(value)}`).join(", ") || "Unknown source";
}
