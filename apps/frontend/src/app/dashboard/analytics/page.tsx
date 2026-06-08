import { BarChart3, Map, TrendingUp, type LucideIcon } from "lucide-react";
import { ScoreBar } from "@/components/atoms/ScoreBar";

// 1. Move the data outside the component to avoid JSX parsing bugs
const INSIGHTS_DATA = [
  ["Salary pressure", "Bengaluru ML roles are up 7% this month.", TrendingUp, 72],
  ["Talent density", "Pune and Hyderabad show the fastest reply velocity.", Map, 84],
  ["Pipeline health", "Shortlist quality is above benchmark for 3 roles.", BarChart3, 91]
] as const;

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
        {/* 2. Map cleanly over the defined array variable */}
        {INSIGHTS_DATA.map(([title, copy, Icon, score]) => {
          // Explicit type casting here ensures Lucide icons render perfectly
          const ComponentIcon = Icon as LucideIcon;
          
          return (
            <section
              className="panel insight-card"
              style={{ gridColumn: "span 4" }}
              key={title}
            >
              <ComponentIcon />
              <h2>{title}</h2>
              <p>{copy}</p>
              <ScoreBar value={score} />
            </section>
          );
        })}
      </div>
    </div>
  );
}
