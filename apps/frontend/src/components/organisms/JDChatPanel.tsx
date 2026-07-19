"use client";

import { JobApi } from "@/lib/api";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

type Msg = { 
  id: string; 
  role: "user" | "bot"; 
  text: string; 
  sourceUserId?: string; 
  originalPrompt?: string; 
};

const COOKING_WORDS = [
  "cooking", "prepping", "marinating", "sautéing", "simmering",
  "baking", "roasting", "seasoning", "reducing", "plating",
];

interface ChatPageProps {
  initialQuery?: string;
}

export function ChatPage({ initialQuery = "" }: ChatPageProps) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [word, setWord] = useState(COOKING_WORDS[0]);
  const logRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);

  // Auto-scroll layout handler
  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  // Loading display text rotating cycle selector
  useEffect(() => {
    if (!loading) return;
    const randomIndex = Math.floor(Math.random() * COOKING_WORDS.length);
    setWord(COOKING_WORDS[randomIndex]);
  }, [loading]);

  // Handle cross-page pipeline routing directly when coming from the JDEditorPanel
  useEffect(() => {
    if (initialQuery.trim()) {
      const userMsgId = crypto.randomUUID();
      
      // Instantly seed the message list so the interface feels lightning-fast
      setMessages([
        { id: userMsgId, role: "user", text: initialQuery.trim() }
      ]);
      
      // Kick off processing automatically
      generateReply(userMsgId, initialQuery.trim());
    }
  }, [initialQuery]);

  // Gracefully clean up dangling socket connection pipes on component destruction
  useEffect(() => {
    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  const generateReply = (sourceUserId: string, description: string) => {
    setLoading(true);
  
    if (socketRef.current) {
      socketRef.current.close();
    }
  
    const ws = JobApi.createJobWebSocket(
      description,
      (data) => {
        if (data.status === "completed") {
          setMessages((m) => [
            ...m,
            { 
              id: crypto.randomUUID(), 
              role: "bot", 
              text: data.result || data.message, // Prioritizes the processed JD markdown content block
              sourceUserId,
              originalPrompt: description // Preserves query context for future retries
            },
          ]);
          setLoading(false);
          ws.close();
        }
      },
      (error) => {
        console.error("WebSocket Error Encountered:", error);
        setLoading(false);
      },
      () => {
        setLoading(false);
      }
    );
  
    socketRef.current = ws;
  };
  
  const send = () => {
    const text = input.trim();
    if (!text || loading) return;
    const userMsg: Msg = { id: crypto.randomUUID(), role: "user", text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    generateReply(userMsg.id, text);
  };

  const retry = (botId: string, sourceUserId?: string) => {
    if (loading) return;
  
    const botMessage = messages.find((x) => x.id === botId);
    const originalPrompt = botMessage?.originalPrompt;
  
    // Purge only the targeted failed generation message context block
    setMessages((m) => m.filter((x) => x.id !== botId));
  
    if (sourceUserId && originalPrompt) {
      generateReply(sourceUserId, originalPrompt);
    }
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
    <div className="chat-wrap" style={{ width: "100%" }}>
      <section className="jd-chat-panel">
        <div className="chat-header">
          <div className="header-meta">NEUROHIRE · CONSOLE</div>
          <div className="header-title-row">
            <h3>Recruiting Copilot</h3>
            <span className="status-badge"><span className="jd-pulse-dot"></span> ONLINE</span>
          </div>
        </div>

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
              <div className="msg-body markdown-content">
                {m.role === "user" ? (
                  <p style={{ margin: 0 }}>{m.text}</p>
                ) : (
                  <ReactMarkdown>{m.text}</ReactMarkdown>
                )}
              </div>
              {m.role === "bot" && m.sourceUserId && (
                <div className="msg-actions">
                  <button className="act act-proceed" onClick={() => proceed(m.id)} disabled={loading}>
                    Proceed
                  </button>
                  <button className="act act-retry" onClick={() => retry(m.id, m.sourceUserId)} disabled={loading}>
                    Retry
                  </button>
                  <button className="act act-delete" onClick={() => remove(m.id)} disabled={loading}>
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
            placeholder="Message the copilot..."
          />
          <button onClick={send} disabled={loading}>SEND</button>
        </div>
      </section>
    </div>
  );
}