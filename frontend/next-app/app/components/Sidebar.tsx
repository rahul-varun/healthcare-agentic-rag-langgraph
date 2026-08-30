"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/documents", label: "Knowledge Base" },
  { href: "/graph", label: "Coverage map" },
  { href: "/evaluation", label: "Quality checks" },
  { href: "/settings", label: "Settings" },
];

function NavIcon({ name }: { name: string }) {
  const paths: Record<string, string> = {
    chat: "M5 6.5h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H12l-4.5 3v-3.1H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2Z",
    documents: "M6 3.5h8l4 4v13H6a2 2 0 0 1-2-2v-13a2 2 0 0 1 2-2Zm8 0v5h4M8 13h8M8 17h6",
    coverage: "M12 3v5m0 8v5M3 12h5m8 0h5M5.6 5.6l3.5 3.5m3.8 3.8 3.5 3.5m0-10.8-3.5 3.5m-3.8 3.8-3.5 3.5",
    quality: "m12 3 7 3v5c0 4.5-2.9 8.3-7 10-4.1-1.7-7-5.5-7-10V6l7-3Zm-3 8 2 2 4-4",
    settings: "M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Zm0-5v2m0 13v2M3.5 12h2m13 0h2M5.3 5.3l1.4 1.4m10.6 10.6 1.4 1.4m0-13.4-1.4 1.4M6.7 17.3l-1.4 1.4",
  };
  return <svg aria-hidden="true" viewBox="0 0 24 24" className="nav-icon" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"><path d={paths[name]} /></svg>;
}

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="care-sidebar flex h-full w-64 flex-shrink-0 flex-col border-r border-white/10 p-5">
      <Link href="/" className="mb-10 flex items-center gap-3 text-sm font-semibold tracking-tight text-white">
        <span className="inline-flex h-9 w-9 items-center justify-center rounded-2xl bg-cyan-300 text-base text-slate-950 shadow-[0_0_24px_rgba(103,232,249,.25)]">✚</span>
        <span>HealthAgent AI <small className="ml-1 block text-[10px] font-normal tracking-[.14em] text-slate-500">HEALTHCARE ASSISTANT</small></span>
      </Link>
      <p className="mb-3 px-3 text-[10px] font-bold tracking-[.18em] text-slate-600">WORKSPACE</p>
      <ul className="flex flex-col gap-1.5">
        <li>
          <Link
            href="/"
            className={`nav-link ${
              pathname === "/" ? "nav-link-active" : "text-slate-400 hover:bg-white/5 hover:text-slate-100"
            }`}
          >
            <span className="nav-glyph"><NavIcon name="chat" /></span>Ask HealthAgent
          </Link>
        </li>
        {NAV_ITEMS.map((item, index) => (
          <li key={`${item.href}-${index}`}>
            <Link
              href={item.href}
              className={`nav-link ${
                pathname === item.href ? "nav-link-active" : "text-slate-400 hover:bg-white/5 hover:text-slate-100"
              }`}
            >
              <span className="nav-glyph"><NavIcon name={item.label === "Knowledge Base" ? "documents" : item.label === "Coverage map" ? "coverage" : item.label === "Quality checks" ? "quality" : "settings"} /></span>{item.label}
            </Link>
          </li>
        ))}
      </ul>
      <div className="mt-auto rounded-2xl border border-cyan-300/10 bg-cyan-300/[.05] p-4">
        <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-cyan-100"><span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]" />Grounded mode on</div>
        <p className="text-[11px] leading-5 text-slate-500">Answers are grounded in your uploaded health documents and trusted sources.</p>
      </div>
    </nav>
  );
}
