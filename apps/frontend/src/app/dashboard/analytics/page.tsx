import { BarChart3, Map, TrendingUp } from "lucide-react";
import { ScoreBar } from "@/components/atoms/ScoreBar";

export default function AnalyticsPage() {
  return (
    <div className="page-pad analytics-page">
      <div className="section-head">
        <div>
          <span>Market Intelligence</span>
          <h1>Hiring Analytics</h1>
        </div>
      </div>
      <div className="dashboard-grid">
        {[
          ["Salary pressure", "Bengaluru ML roles are up 7% this month.", TrendingUp, 72],
          ["Talent density", "Pune and Hyderabad show the fastest reply velocity.", Map, 84],
          ["Pipeline health", "Shortlist quality is above benchmark for 3 roles.", BarChart3, 91]
        ].map(([title, copy, Icon, score]) => {
          const TypedIcon = Icon as typeof BarChart3;
          return (
            <section className="panel insight-card" style={{ gridColumn: "span 4" }} key={title as string}>
              <TypedIcon />
              <h2>{title}</h2>
              <p>{copy}</p>
              <ScoreBar value={score as number} />
            </section>
          );
        })}
      </div>
    </div>
  );
}
