"use client";

import { useEffect, useState } from "react";
import { ArrowRight, CircleAlert, CircleCheckBig, RotateCcw, Square, Sparkles, ShieldAlert, Check } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/atoms/Button";
import { ScoreGauge } from "@/components/molecules/ScoreGauge";
import { JobApi } from "@/lib/api";
import { useRouter } from "next/dist/client/components/navigation";

type ReviewAction = "retry" | "continue" | "stop" | null;
type PostingChannel = "naukri" | "linkedin" | "indeed";

interface EscalationDetails {
  escalation_id: string;
  timestamp: string;
  severity: string;
  bias_score: number;
  threshold: number;
  score_exceeded_by: number;
  flagged_words_count: number;
  detailed_analysis: {
    summary: string;
    word_frequency_analysis: Record<string, { count: number; suggestion: string }>;
    patterns_detected: string[];
    impact_assessment: string;
  };
  actionable_recommendations: Array<{ priority: string; action: string }>;
  urgency: string;
}

interface BiasData {
  flagged_words: string[];
  replacement_suggestions: string[];
  bias_score: number;
  recommendation: string;
  escalated: boolean;
  escalation_details?: EscalationDetails;
}

type JobSessionWithBias = Awaited<ReturnType<typeof JobApi.getJobStatus>> & Partial<BiasData>;
type JobPipelineWithBias = Awaited<ReturnType<typeof JobApi.createJob>> & Partial<BiasData>;

const router = useRouter();
const sessionStorageKey = "neuro-hire.job.session-id";
const postingChannels: Array<{ key: PostingChannel; label: string; hint: string }> = [
  { key: "naukri", label: "Naukri.com", hint: "Primary India hiring board" },
  { key: "linkedin", label: "LinkedIn", hint: "Professional network reach" },
  { key: "indeed", label: "Indeed", hint: "High-volume job discovery" }
];

export function JDEditorPanel() {
  const [query, setQuery] = useState<string>(
    "Senior backend engineer for AI recruiting platform. Needs Python, FastAPI, vector search, AWS, strong mentorship, remote friendly, inclusive wording, salary 40-60 LPA."
  );
  const [liveDeiScore, setLiveDeiScore] = useState<number>(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<string>("idle");
  const [currentDraft, setCurrentDraft] = useState<string>("");
  const [reviewAction, setReviewAction] = useState<ReviewAction>(null);
  const [feedback, setFeedback] = useState<string>("");
  const [selectedChannels, setSelectedChannels] = useState<PostingChannel[]>(["naukri", "linkedin"]);
  const [message, setMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [biasData, setBiasData] = useState<BiasData | null>(null);
  const liveDeiTone = liveDeiScore >= 80 ? "good" : liveDeiScore >= 60 ? "warning" : "danger";

  useEffect(() => {
    const savedSessionId = window.localStorage.getItem(sessionStorageKey);
    if (savedSessionId) {
      setSessionId(savedSessionId);
    }
  }, []);

  useEffect(() => {
    if (!sessionId) {
      window.localStorage.removeItem(sessionStorageKey);
      return;
    }

    window.localStorage.setItem(sessionStorageKey, sessionId);
  }, [sessionId]);

  useEffect(() => {
    if (!query.trim()) {
      setLiveDeiScore(0);
      return;
    }

    const delayDebounceFn = window.setTimeout(async () => {
      try {
        const data = await JobApi.getDEIScore(query);
        const liveData = data.dei_score;
        const normalizedLiveScore =
          typeof liveData.dei_score === "number"
            ? liveData.dei_score
            : typeof liveData.bias_score === "number"
              ? Math.max(0, Math.min(100, 100 - liveData.bias_score))
              : 0;

        setLiveDeiScore(normalizedLiveScore);
        setBiasData({
          flagged_words: Array.isArray(liveData.flagged_words) ? liveData.flagged_words : [],
          replacement_suggestions: Array.isArray(liveData.replacement_suggestions) ? liveData.replacement_suggestions : [],
          bias_score: typeof liveData.bias_score === "number" ? liveData.bias_score : 100 - normalizedLiveScore,
          recommendation: typeof liveData.recommendation === "string" ? liveData.recommendation : "",
          escalated: Boolean(liveData.escalated),
          escalation_details: liveData.escalation_details as EscalationDetails | undefined
        });
      } catch (error) {
        console.error("Failed to fetch live DEI score", error);
      }
    }, 500);

    return () => window.clearTimeout(delayDebounceFn);
  }, [query]);

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    let isMounted = true;

    const refreshSession = async () => {
      try {
        const data = (await JobApi.getJobStatus(sessionId)) as JobSessionWithBias;

        if (!isMounted) {
          return;
        }

        setSessionStatus(data.status);
        setCurrentDraft(data.current_draft || data.raw_draft || data.raw_input || "");

        if (Array.isArray(data.flagged_words) && data.flagged_words.length > 0) {
          setBiasData({
            flagged_words: data.flagged_words,
            replacement_suggestions: data.replacement_suggestions ?? [],
            bias_score: typeof data.bias_score === "number" ? data.bias_score : 0,
            recommendation: data.recommendation ?? "",
            escalated: Boolean(data.escalated),
            escalation_details: data.escalation_details
          });
        }

        if (data.status !== "awaiting_human_review") {
          setReviewAction(null);
        }
      } catch (error) {
        if (isMounted) {
          console.error("Failed to refresh job session", error);
        }
      }
    };

    refreshSession();
    const timer = window.setInterval(refreshSession, 4500);

    return () => {
      isMounted = false;
      window.clearInterval(timer);
    };
  }, [sessionId]);

  const startJob = async () => {
    if (!query.trim()) {
      setMessage("Add a prompt before generating a JD.");
      return;
    }

    setIsLoading(true);
    setMessage("");
    setBiasData(null);

    try {
      const response = (await JobApi.createJob({ description_query: query })) as JobPipelineWithBias;
      setSessionId(response.session_id);
      setSessionStatus(response.status);
      setMessage(response.message);

      if (Array.isArray(response.flagged_words) && response.flagged_words.length > 0) {
        setBiasData({
          flagged_words: response.flagged_words,
          replacement_suggestions: response.replacement_suggestions ?? [],
          bias_score: typeof response.bias_score === "number" ? response.bias_score : 0,
          recommendation: response.recommendation ?? "",
          escalated: Boolean(response.escalated),
          escalation_details: response.escalation_details
        });
      }
    } catch (error) {
      setMessage("Unable to start the JD pipeline right now.");
      console.error("Failed to create job", error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFix = (flagged: string, replacement: string) => {
    const regex = new RegExp(`\\b${flagged}\\b`, "gi");
    setQuery((prev) => prev.replace(regex, replacement));
    setBiasData(null);
  };

  const openReviewAction = (action: Exclude<ReviewAction, null>) => {
    if (!sessionId) {
      setMessage("Start a job first to open HITL controls.");
      return;
    }

    setReviewAction(action);
    setMessage("");
  };

  const submitReviewAction = async (action: Exclude<ReviewAction, null>) => {
    if (!sessionId) {
      setMessage("Start a job first to open HITL controls.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await JobApi.reviewJob({
        session_id: sessionId,
        approved: action === "continue",
        action,
        feedback: action === "retry" ? feedback : undefined,
        selected_channels: action === "continue" ? selectedChannels : undefined
      });

      setMessage(response.message);
      setSessionStatus(response.status);
      setReviewAction(null);

      if (action === "stop") {
        setCurrentDraft("");
        setBiasData(null);
      }

      if (action === "retry") {
        setFeedback("");
      }
    } catch (error) {
      setMessage("The HITL action could not be completed.");
      console.error("Failed to submit human review", error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleChannel = (channel: PostingChannel) => {
    setSelectedChannels((current) =>
      current.includes(channel) ? current.filter((entry) => entry !== channel) : [...current, channel]
    );
  };

  return (
    <div className="jd-shell">
      <section className="panel jd-editor">
        <div className="section-head jd-editor-head">
          <div>
            <span>JD Architect</span>
            <h2>New Job Requisition</h2>
          <Button icon={<Sparkles size={16} />} onClick={startJob} disabled={isLoading}>
            {isLoading && !sessionId ? "Launching..." : "Generate JD"}
          </Button>
          </Button>
        </div>

        <div className="jd-main-grid">
          <div className="jd-editor-column">
            <label className="jd-label" htmlFor="job-prompt">
              Prompt
            </label>
            <textarea
              id="job-prompt"
              className="jd-textarea"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your prompt or draft your JD here..."
            />

            <div className="jd-meta-row">
              <span className={`nh-badge nh-badge-${liveDeiTone}`}>Live DEI {Math.round(liveDeiScore)}/100</span>
              <span className="nh-badge nh-badge-neutral">Session {sessionId ? sessionId.slice(0, 8) : "pending"}</span>
              <span className="nh-badge nh-badge-good">Status {sessionStatus}</span>
            </div>

            {message && <div className="jd-alert">{message}</div>}

            {biasData && (
              <div
                className="jd-bias-banner"
                style={{
                  background:
                    biasData.bias_score >= 80
                      ? "rgba(126, 231, 135, 0.08)"
                      : biasData.bias_score >= 60
                        ? "rgba(255, 188, 115, 0.10)"
                        : "rgba(255, 143, 163, 0.10)",
                  border:
                    biasData.bias_score >= 80
                      ? "1px solid rgba(126, 231, 135, 0.35)"
                      : biasData.bias_score >= 60
                        ? "1px solid rgba(255, 188, 115, 0.38)"
                        : "1px solid rgba(255, 143, 163, 0.4)",
                  padding: "12px",
                  borderRadius: "10px",
                  margin: "12px 0"
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    fontWeight: "700",
                    color: biasData.bias_score >= 80 ? "var(--green)" : biasData.bias_score >= 60 ? "var(--amber)" : "var(--rose)",
                    fontSize: "14px",
                    lineHeight: 1.2
                  }}
                >
                  <ShieldAlert size={18} />
                  <span>Bias Guardian Warning (Score: {biasData.bias_score.toFixed(1)}%)</span>
                </div>
                <p style={{ fontSize: "13px", lineHeight: 1.55, margin: "8px 0 10px 0", color: "var(--text)" }}>{biasData.recommendation}</p>

                {biasData.flagged_words.length > 0 ? (
                  <>
                    {biasData.escalation_details?.detailed_analysis.patterns_detected.map((pattern, idx) => (
                      <span key={idx} className="nh-badge nh-badge-danger" style={{ fontSize: "11px", marginRight: "4px" }}>
                        {pattern}
                      </span>
                    ))}

                    <div style={{ marginTop: "12px", display: "flex", gap: "8px", flexDirection: "column" }}>
                      {biasData.flagged_words.map((word, index) => (
                        <div
                          key={index}
                          style={{ display: "flex", alignItems: "center", justifyContent: "space-between", background: "#fff", padding: "6px 10px", borderRadius: "4px", border: "1px solid #e5e7eb" }}
                        >
                          <span style={{ fontSize: "13px" }}>
                            Replace <strong style={{ color: "#ef4444" }}>{`"${word}"`}</strong> with <strong style={{ color: "#16a34a" }}>{`"${biasData.replacement_suggestions[index] ?? word}"`}</strong>
                          </span>
                          <Button
                            variant="ghost"
                            icon={<Check size={14} />}
                            onClick={() => applyFix(word, biasData.replacement_suggestions[index] ?? word)}
                          >
                            Apply Fix
                          </Button>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <p style={{ fontSize: "13px", margin: "8px 0 0 0", color: "#6b7280" }}>No flagged terms detected in the current draft.</p>
                )}

                <div style={{ marginTop: "12px", display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  <Button variant="ghost" icon={<RotateCcw size={14} />} onClick={() => openReviewAction("retry")} disabled={!sessionId || isLoading}>
                    Request Retry
                  </Button>
                  <Button icon={<ArrowRight size={14} />} onClick={() => openReviewAction("continue")} disabled={!sessionId || isLoading}>
                    Continue to Publish
                  </Button>
                  <Button variant="danger" icon={<Square size={14} />} onClick={() => openReviewAction("stop")} disabled={!sessionId || isLoading}>
                    Stop Pipeline
                  </Button>
                </div>
              </div>
            )}

            {currentDraft && (
              <div className="jd-draft-card">
                <div className="jd-draft-card-head">
                  <strong>Current draft</strong>
                  {sessionStatus === "processing" && <span className="nh-badge nh-badge-info">Processing</span>}
                </div>
                <p>{currentDraft}</p>
              </div>
            )}

            <div className="jd-insight-copy">
              <strong>Market intelligence</strong>
              <p>Recommended range: Rs. 42L-62L. Talent availability is moderate, with stronger pools in Bengaluru and Pune.</p>
              {biasData?.escalation_details ? (
                <p style={{ color: "#b91c1c" }}>
                  <strong>System Notice:</strong> {biasData.escalation_details.detailed_analysis.impact_assessment}
                </p>
              ) : (
                <p>Bias Guardian removed aggressive terms and improved remote work clarity.</p>
              )}
            </div>

            {reviewAction && (
              <motion.div
                className="hitl-subpanel"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                <strong>
                  {reviewAction === "retry" && "Retry review"}
                  {reviewAction === "continue" && "Publish review"}
                  {reviewAction === "stop" && "Stop pipeline"}
                </strong>

                {reviewAction === "retry" && (
                  <textarea
                    className="jd-textarea jd-textarea-small"
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    placeholder="Tell the system what to improve before retrying."
                  />
                )}

                {reviewAction === "continue" && (
                  <div className="channel-grid">
                    {postingChannels.map((channel) => (
                      <button
                        key={channel.key}
                        type="button"
                        className={`channel-card ${selectedChannels.includes(channel.key) ? "is-selected" : ""}`}
                        onClick={() => toggleChannel(channel.key)}
                      >
                        <strong>{channel.label}</strong>
                        <small>{channel.hint}</small>
                      </button>
                    ))}
                  </div>
                )}

                <div className="hitl-footer">
                  <Button
                    icon={reviewAction === "retry" ? <RotateCcw size={14} /> : reviewAction === "continue" ? <CircleCheckBig size={14} /> : <CircleAlert size={14} />}
                    onClick={() => submitReviewAction(reviewAction as Exclude<ReviewAction, null>)}
                    disabled={isLoading}
                  >
                    {isLoading ? "Submitting..." : "Confirm Action"}
                  </Button>
                  <Button variant="ghost" onClick={() => setReviewAction(null)} disabled={isLoading}>
                    Cancel
                  </Button>
                </div>
              </motion.div>
            )}
          </div>

          <div className="jd-insight-column">
            <div className="jd-insight-copy">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", marginBottom: "12px" }}>
                <div>
                  <strong>Live DEI signal</strong>
                  <p>Tracked against the current prompt and bias corrections.</p>
                </div>
                <ScoreGauge value={liveDeiScore} label="DEI" />
              </div>
              <p>Use the prompt editor to tune language, then publish or route through HITL controls.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
