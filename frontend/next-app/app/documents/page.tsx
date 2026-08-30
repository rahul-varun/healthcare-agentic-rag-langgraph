"use client";

import { useEffect, useState } from "react";
import { ApiError, DocumentInfo, listDocuments, uploadDocument } from "../lib/api";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentInfo[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setUploading(true); setError(null); setUploadMessage(null);
    try {
      const result = await uploadDocument(file);
      setUploadMessage(`${result.name} indexed successfully (${result.chunks} sections)`);
      setDocuments((await listDocuments()).documents);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    } finally { setUploading(false); }
  }

  useEffect(() => {
    listDocuments()
      .then((res) => setDocuments(res.documents))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load documents"));
  }, []);

  return (
    <div className="mx-auto max-w-5xl p-6 md:p-10">
      <div className="mb-8 flex items-end justify-between gap-4">
        <div><p className="eyebrow">Knowledge center</p><h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">Your health knowledge</h1>
        <p className="mt-2 text-sm text-slate-400">Upload policy documents, health cards, and benefit guides to make them searchable.</p></div>
        <label className="button-primary cursor-pointer whitespace-nowrap"><span>{uploading ? "Indexing…" : "＋ Upload document"}</span><input type="file" accept=".pdf,.md,.markdown,application/pdf,text/markdown" onChange={handleUpload} disabled={uploading} className="hidden" /></label>
      </div>

      <div className="upload-panel mb-8">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-400/10 text-xl text-cyan-300">↑</div>
        <div><h2 className="font-medium text-white">Add to your knowledge base</h2><p className="mt-1 text-sm text-slate-400">PDF, Markdown · up to 25 MB · text is indexed automatically</p></div>
        <label className="button-secondary ml-auto cursor-pointer">Choose file<input type="file" accept=".pdf,.md,.markdown,application/pdf,text/markdown" onChange={handleUpload} disabled={uploading} className="hidden" /></label>
      </div>

      {error && (
        <div className="mt-4 rounded-md border border-red-900 bg-red-950/50 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}
      {uploadMessage && <div className="mb-4 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-300">✓ {uploadMessage}</div>}

      {!error && !documents && <p className="mt-6 text-sm text-neutral-500">Loading…</p>}

      {documents && documents.length === 0 && (
        <p className="mt-6 text-sm text-slate-500">No documents yet. Upload your first health policy or benefits PDF.</p>
      )}

      {documents && documents.length > 0 && (
        <div className="document-library surface mt-6 overflow-hidden">
          <div className="flex items-center justify-between border-b border-white/10 px-5 py-4"><div><h2 className="text-sm font-semibold text-white">Indexed documents</h2><p className="mt-1 text-xs text-slate-500">{documents.length} source{documents.length === 1 ? "" : "s"} available to HealthAgent AI</p></div><span className="rounded-full bg-emerald-400/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-emerald-300">Live index</span></div>
          <table className="w-full border-collapse text-left text-sm">
            <thead><tr className="border-b border-white/10 text-[10px] uppercase tracking-[.14em] text-slate-600"><th className="px-5 py-3 font-semibold">Document</th><th className="px-4 py-3 font-semibold">Format</th><th className="px-4 py-3 font-semibold">Size</th><th className="px-5 py-3 text-right font-semibold">Status</th></tr></thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.relative_path} className="document-row text-slate-200">
                  <td className="px-5 py-4"><div className="flex min-w-0 items-center gap-3"><span className={`file-badge ${doc.type === "pdf" ? "file-badge-pdf" : "file-badge-md"}`}>{doc.type === "pdf" ? "PDF" : "MD"}</span><div className="min-w-0"><p className="truncate font-medium text-slate-100">{doc.name}</p><p className="mt-1 truncate text-[11px] text-slate-600">{doc.relative_path}</p></div></div></td>
                  <td className="px-4 py-4 uppercase text-slate-500">{doc.type}</td>
                  <td className="px-4 py-4 text-slate-400">{formatBytes(doc.size_bytes)}</td>
                  <td className="px-5 py-4 text-right"><span className="inline-flex items-center gap-1.5 text-xs text-emerald-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Indexed</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
