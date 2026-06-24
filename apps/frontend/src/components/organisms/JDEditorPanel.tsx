"use client";

import { useState , useEffect } from "react";
import { WandSparkles } from "lucide-react";
import { Button } from "@/components/atoms/Button";
import { ScoreGauge } from "@/components/molecules/ScoreGauge";
import { JobApi } from "@/lib/api";
const sample = "Senior backend engineer for AI recruiting platform. Needs Python, FastAPI, vector search, AWS, strong mentorship, remote friendly, inclusive wording, salary 40-60 LPA.";

export function JDEditorPanel() {
  const [query, setQuery] = useState<string>('');
  const [liveDeiScore, setLiveDeiScore] = useState<number>(0);
  useEffect(() => {
    // 1. Don't hit the server if the input is empty
    if (!query.trim()) {
      setLiveDeiScore(0);
      return;
    }

    // 2. Set up a debounce timer
    const delayDebounceFn = setTimeout(async () => {
      try {
        const response = await JobApi.getDEIScore(query);
        const data = await response.json();
        setLiveDeiScore(data.dei_score);
      } catch (error) {
        console.error("Failed to fetch live DEI score", error);
      }
    }, 500); // 500ms delay: waits until user pauses typing

    // 3. Clean up the timer if the user types another character before 500ms
    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  return (
    <div className="jd-grid">
      <section className="panel jd-editor">
        <div className="section-head">
          <div>
            <span>JD Architect</span>
            <h2>New Job Requisition</h2>
          </div>
          <Button icon={<WandSparkles size={16} />}>Generate JD</Button>
        </div>
        <div>
          <textarea 
          value={query} 
          onChange={(e) => setQuery(e.target.value)} 
          placeholder="Type your prompt or draft your JD here..."
          />
        <div>Live DEI Prediction: {liveDeiScore}/100</div>
    </div>
        <div className="data-rail" />
      </section>
      <section className="panel intelligence-panel">
        <ScoreGauge value={liveDeiScore} label="JD Quality" />
        <h3>Market intelligence</h3>
        <p>Recommended range: Rs. 42L-62L. Talent availability is moderate, with stronger pools in Bengaluru and Pune.</p>
        <p>Bias Guardian removed aggressive terms and improved remote work clarity.</p>
      </section>
    </div>
  );
}
