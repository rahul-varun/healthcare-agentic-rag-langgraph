"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function normalizeMarkdown(value: string): string {
  // Some model responses escape Markdown punctuation (\\# and \\*\\*).
  // Normalize only Markdown markers; keep meaningful backslashes untouched.
  return value.replace(/\\([#*_~])/g, "$1");
}

export default function MarkdownContent({ content }: { content: string }) {
  return (
    <div className="medical-markdown">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{normalizeMarkdown(content)}</ReactMarkdown>
    </div>
  );
}
