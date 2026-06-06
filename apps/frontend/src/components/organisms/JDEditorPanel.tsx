"use client";

import { useState } from "react";
import { WandSparkles } from "lucide-react";
import { Button } from "@/components/atoms/Button";
import { ScoreGauge } from "@/components/molecules/ScoreGauge";

const sample = "Senior backend engineer for AI recruiting platform. Needs Python, FastAPI, vector search, AWS, strong mentorship, remote friendly, inclusive wording, salary 40-60 LPA.";

export function JDEditorPanel() {
  const [text, setText] = useState(sample);
  const score = Math.min(99, 72 + Math.floor(text.length / 12));

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
        <textarea value={text} onChange={(event) => setText(event.target.value)} />
        <div className="data-rail" />
      </section>
      <section className="panel intelligence-panel">
        <ScoreGauge value={score} label="JD Quality" />
        <h3>Market intelligence</h3>
        <p>Recommended range: Rs. 42L-62L. Talent availability is moderate, with stronger pools in Bengaluru and Pune.</p>
        <p>Bias Guardian removed aggressive terms and improved remote work clarity.</p>
      </section>
    </div>
  );
}
