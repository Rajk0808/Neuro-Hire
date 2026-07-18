"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  BarChart3,
  BriefcaseBusiness,
  CalendarCheck,
  LayoutDashboard,
  Plus,
  Search,
  Users,
} from "lucide-react";

// --- Utility function for rendering mock bold text safely ---
function renderBold(text: string) {
  if (!text) return "";
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

type Msg = { id: string; role: "user" | "bot"; text: string; sourceUserId?: string };

const COOKING_WORDS = [
  "cooking", "prepping", "marinating", "sautéing", "simmering",
  "baking", "roasting", "seasoning", "reducing", "plating",
];

const MOCK_REPLIES = [
  "**Senior Frontend Engineer** — React / TypeScript\n\n• 5+ yrs shipping production UIs\n• Strong systems thinking, design taste\n• Comfortable with SSR, edge runtimes\n• Hybrid, competitive comp band",
  "**Staff ML Engineer** — Retrieval & Ranking\n\n• Owns candidate-matching pipeline\n• Python, vector DBs, LLM eval\n• Partners with recruiting ops\n• Remote-friendly",
  "**Product Designer** — Recruiting Copilot\n\n• Craft-first, systems-minded\n• Prototypes in code a plus\n• Works directly with founders",
  "**Backend Engineer** — Pipelines & APIs\n\n• FastAPI, Postgres, Neo4j\n• Async workflows, graph modeling\n• Ships end-to-end",
  "**Recruiting Ops Lead** — Pipeline Health\n\n• Owns funnel metrics\n• Automations across ATS + outreach\n• Analytical, low-ego",
];

const NAV = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { key: "jobs", label: "Jobs", icon: BriefcaseBusiness },
  { key: "candidates", label: "Candidates", icon: Users },
  { key: "interviews", label: "Interviews", icon: CalendarCheck },
  { key: "analytics", label: "Analytics", icon: BarChart3 },
];

export function ChatPage() {
  // 1. Instantiating router cleanly at the top-level of the component function
  const router = useRouter();

  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [word, setWord] = useState(COOKING_WORDS[0]);
  const [active, setActive] = useState("console");
  const [navOpen, setNavOpen] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>(([]));

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) return;
    let i = 0;
    setWord(COOKING_WORDS[0]);
    const iv = setInterval(() => {
      i = (i + 1) % COOKING_WORDS.length;
      setWord(COOKING_WORDS[i]);
    }, 700);
    return () => clearInterval(iv);
  }, [loading]);

  useEffect(() => () => timers.current.forEach(clearTimeout), []);

  const generateReply = (sourceUserId: string) => {
    setLoading(true);
    const delay = 2800 + Math.random() * 2200;
    const t = setTimeout(() => {
      const reply = MOCK_REPLIES[Math.floor(Math.random() * MOCK_REPLIES.length)];
      setMessages((m) => [
        ...m,
        { id: crypto.randomUUID(), role: "bot", text: reply, sourceUserId },
      ]);
      setLoading(false);
    }, delay);
    timers.current.push(t);
  };

  const send = () => {
    const text = input.trim();
    if (!text || loading) return;
    const userMsg: Msg = { id: crypto.randomUUID(), role: "user", text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    generateReply(userMsg.id);
  };

  const retry = (botId: string, sourceUserId?: string) => {
    if (loading) return;
    setMessages((m) => m.filter((x) => x.id !== botId));
    if (sourceUserId) generateReply(sourceUserId);
  };

  const remove = (botId: string) => {
    if (loading) return;
    setMessages((m) => m.filter((x) => x.id !== botId));
  };

  const proceed = (botId: string) => {
    if (loading) return;
    const note: Msg = {
      id: crypto.randomUUID(),
      role: "bot",
      text: "✓ Proceeding with this JD — routed to pipeline builder.",
    };
    setMessages((m) => [...m, note]);
    void botId;
  };

  const onKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="app-shell">
      <aside className={`dash-sidebar ${navOpen ? "open" : ""}`}>
        {/* 2. Converted standard anchor tag to Next.js <Link> wrapper */}
        <Link className="brand" href="/">
          <span>NH</span>
          <div>
            <strong>NeuroHire</strong>
            <small>Autonomous Intelligence</small>
          </div>
        </Link>
        <nav>
          {NAV.map((n) => {
            const Icon = n.icon;
            return (
              <button
                key={n.key}
                className={active === n.key ? "active" : ""}
                onClick={() => {
                  setActive(n.key);
                  setNavOpen(false);
                }}
              >
                <Icon size={18} />
                {n.label}
              </button>
            );
          })}
        </nav>
        <button
          className="sidebar-action"
          onClick={() => {
            // 3. Removed illegal inner callback initialization
            router.push("/dashboard/jobs/new");
          }}
        >
          <Plus size={16} />
          New requisition
        </button>
      </aside>

      <main className="dash-main">
        <header className="dash-top">
          <button
            className="nav-toggle"
            aria-label="Toggle navigation"
            onClick={() => setNavOpen((v) => !v)}
          >
            <span /><span /><span />
          </button>
          <div className="search-bar">
            <Search size={16} />
            <input placeholder="Search candidates, jobs, pipelines…" />
          </div>
          <div className="top-status"><span className="pulse-dot" /> {word}... 8 agents online</div>
        </header>

        <div className="chat-wrap">
          <section className="chat-panel">
            <header className="chat-head">
              <div className="brand-head">
                <span className="dot" />
                <div>
                  <div className="eyebrow">NeuroHire · Console</div>
                  <h1>Recruiting Copilot</h1>
                </div>
              </div>
              <span className="eyebrow" style={{ color: "var(--muted)" }}>
                {loading ? "processing" : "online"}
              </span>
            </header>

            <div className="chat-log" ref={logRef}>
              {messages.length === 0 && !loading && (
                <div className="empty">
                  <h2>Ready when you are.</h2>
                  <p>Ask about candidates, pipelines, or job descriptions.</p>
                </div>
              )}

              {messages.map((m) => (
                <div key={m.id} className={`msg ${m.role}`}>
                  <span className="role">{m.role === "user" ? "You" : "NeuroHire"}</span>
                  <div className="msg-body">
                    {m.text.split("\n").map((line, i) => (
                      <p key={i} style={{ margin: "0 0 4px" }}>
                        {renderBold(line)}
                      </p>
                    ))}
                  </div>
                  {m.role === "bot" && m.sourceUserId && (
                    <div className="msg-actions">
                      <button
                        className="act act-proceed"
                        onClick={() => proceed(m.id)}
                        disabled={loading}
                      >
                        Proceed
                      </button>
                      <button
                        className="act act-retry"
                        onClick={() => retry(m.id, m.sourceUserId)}
                        disabled={loading}
                      >
                        Retry
                      </button>
                      <button
                        className="act act-delete"
                        onClick={() => remove(m.id)}
                        disabled={loading}
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              ))}
              {loading && <div className="loading-indicator">{word}...</div>}
            </div>
            
            <div className="chat-input-area">
              <textarea 
                value={input} 
                onChange={(e) => setInput(e.target.value)} 
                onKeyDown={onKey}
                placeholder="Type your message..."
              />
              <button onClick={send} disabled={loading}>Send</button>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
