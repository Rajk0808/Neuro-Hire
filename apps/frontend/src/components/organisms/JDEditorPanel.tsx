"use client";

import { useEffect, useState } from "react";
import { ArrowRight, CircleAlert, CircleCheckBig, RotateCcw, Square, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/atoms/Button";
import { ScoreGauge } from "@/components/molecules/ScoreGauge";
import { JobApi } from "@/lib/api";

type ReviewAction = "retry" | "continue" | "stop" | null;
type PostingChannel = "naukri" | "linkedin" | "indeed";

const sessionStorageKey = "neuro-hire.job.session-id";
const postingChannels: Array<{ key: PostingChannel; label: string; hint: string }> = [
  { key: "naukri", label: "Naukri.com", hint: "Primary India hiring board" },
  { key: "linkedin", label: "LinkedIn", hint: "Professional network reach" },
  { key: "indeed", label: "Indeed", hint: "High-volume job discovery" }
];

export function JDEditorPanel() {
  const [query, setQuery] = useState<string>("Senior backend engineer for AI recruiting platform. Needs Python, FastAPI, vector search, AWS, strong mentorship, remote friendly, inclusive wording, salary 40-60 LPA.");
  const [liveDeiScore, setLiveDeiScore] = useState<number>(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<string>("idle");
  const [currentDraft, setCurrentDraft] = useState<string>("");
  const [reviewAction, setReviewAction] = useState<Exclude<ReviewAction, null> | null>(null);
  const [feedback, setFeedback] = useState<string>("");
  const [selectedChannels, setSelectedChannels] = useState<PostingChannel[]>(["naukri", "linkedin"]);
  const [message, setMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

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
    // 1. Don't hit the server if the input is empty
    if (!query.trim()) {
      setLiveDeiScore(0);
      return;
    }

    // 2. Set up a debounce timer
    const delayDebounceFn = setTimeout(async () => {
      try {
        const data = await JobApi.getDEIScore(query);
        setLiveDeiScore(data.dei_score);
      } catch (error) {
        console.error("Failed to fetch live DEI score", error);
      }
    }, 500); // 500ms delay: waits until user pauses typing

    // 3. Clean up the timer if the user types another character before 500ms
    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    let isMounted = true;

    const refreshSession = async () => {
      try {
        const data = await JobApi.getJobStatus(sessionId);

        if (!isMounted) {
          return;
        }

        setSessionStatus(data.status);
        setCurrentDraft(data.current_draft || data.raw_draft || data.raw_input || "");

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

    try {
      const response = await JobApi.createJob({ jd_query: query });
      setSessionId(response.session_id);
      setSessionStatus(response.status);
      setMessage(response.message);
    } catch (error) {
      setMessage("Unable to start the JD pipeline right now.");
      console.error("Failed to create job", error);
    } finally {
      setIsLoading(false);
    }
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
          </div>
          <Button icon={<Sparkles size={16} />} onClick={startJob} disabled={isLoading}>
            {isLoading && !sessionId ? "Launching..." : "Generate JD"}
          </Button>
        </div>

        <div className="jd-main-grid">
          <div className="jd-editor-column">
            <label className="jd-label" htmlFor="job-prompt">Prompt</label>
            <textarea
              id="job-prompt"
              className="jd-textarea"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your prompt or draft your JD here..."
            />

            <div className="jd-meta-row">
              <span className="nh-badge nh-badge-info">Live DEI {liveDeiScore}/100</span>
              <span className="nh-badge nh-badge-neutral">Session {sessionId ? sessionId.slice(0, 8) : "pending"}</span>
              <span className="nh-badge nh-badge-good">Status {sessionStatus}</span>
            </div>

            {message && <div className="jd-alert">{message}</div>}

            {currentDraft && (
              <div className="jd-draft-card">
                <div className="jd-draft-card-head">
                  <strong>Current draft</strong>
                  {sessionStatus === "processing" && <span className="jd-live-dot" />}
                </div>
                <p>{currentDraft}</p>
              </div>
            )}
          </div>

          <div className="jd-insight-column">
            <ScoreGauge value={liveDeiScore} label="JD Quality" />
            <div className="jd-insight-copy">
              <h3>Market intelligence</h3>
              <p>Recommended range: Rs. 42L-62L. Talent availability is moderate, with stronger pools in Bengaluru and Pune.</p>
              <p>Bias Guardian removed aggressive terms and improved remote work clarity.</p>
            </div>
          </div>
        </div>

        <div className="data-rail" />
      </section>

      <section className="panel hitl-panel">
        <div className="section-head hitl-head">
          <div>
            <span>Human in the loop</span>
            <h3>Hold the screen, choose the next step</h3>
          </div>
          <CircleAlert size={18} />
        </div>

        <div className="hitl-actions">
          <Button variant="danger" icon={<RotateCcw size={16} />} onClick={() => openReviewAction("retry")} disabled={!sessionId || isLoading}>
            Retry
          </Button>
          <Button icon={<CircleCheckBig size={16} />} onClick={() => openReviewAction("continue")} disabled={!sessionId || isLoading}>
            Continue
          </Button>
          <Button variant="ghost" icon={<Square size={16} />} onClick={() => void submitReviewAction("stop")} disabled={!sessionId || isLoading}>
            Stop
          </Button>
        </div>

        <motion.div
          className="hitl-reveal"
          animate={{ height: reviewAction ? "auto" : 0, opacity: reviewAction ? 1 : 0 }}
          transition={{ duration: 0.22 }}
        >
          {reviewAction === "retry" && (
            <div className="hitl-subpanel">
              <label className="jd-label" htmlFor="retry-feedback">Retry feedback</label>
              <textarea
                id="retry-feedback"
                className="jd-textarea jd-textarea-small"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Tell the agent what to change in the JD..."
              />
              <Button icon={<ArrowRight size={16} />} onClick={() => void submitReviewAction("retry")} disabled={isLoading || !feedback.trim()}>
                Regenerate draft
              </Button>
            </div>
          )}

          {reviewAction === "continue" && (
            <div className="hitl-subpanel">
              <div className="channel-grid">
                {postingChannels.map((channel) => {
                  const isSelected = selectedChannels.includes(channel.key);

                  return (
                    <button
                      key={channel.key}
                      type="button"
                      className={`channel-card ${isSelected ? "is-selected" : ""}`}
                      onClick={() => toggleChannel(channel.key)}
                    >
                      <span>{channel.label}</span>
                      <small>{channel.hint}</small>
                    </button>
                  );
                })}
              </div>
              <Button icon={<ArrowRight size={16} />} onClick={() => void submitReviewAction("continue")} disabled={isLoading || selectedChannels.length === 0}>
                Publish to selected channels
              </Button>
            </div>
          )}
        </motion.div>

        <div className="hitl-footer">
          <span className="nh-badge nh-badge-neutral">Same window, no navigation</span>
          <span className="nh-badge nh-badge-info">Session stored locally</span>
        </div>
      </section>
    </div>
  );
}
