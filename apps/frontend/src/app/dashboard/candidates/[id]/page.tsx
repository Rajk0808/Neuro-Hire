import { notFound } from "next/navigation";
import { Badge } from "@/components/atoms/Badge";
import { ScoreGauge } from "@/components/molecules/ScoreGauge";
import { candidates } from "@/lib/mockData";

export default async function CandidateDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const candidate = candidates.find((item) => item.id === id);
  if (!candidate) notFound();

  return (
    <div className="page-pad detail-page">
      <section className="panel detail-hero">
        <Badge label={candidate.status} />
        <h1>{candidate.name}</h1>
        <p>{candidate.current_role} at {candidate.current_company} · {candidate.location}</p>
        <div className="chip-row">{candidate.skills.map((skill) => <span key={skill}>{skill}</span>)}</div>
      </section>
      <div className="dashboard-grid">
        <section className="panel" style={{ gridColumn: "span 4", padding: 24 }}>
          <ScoreGauge value={Math.round(candidate.retrieval_scores.rrf_score * 100)} label="Match" />
        </section>
        <section className="panel profile-panel" style={{ gridColumn: "span 8" }}>
          <h2>Agent summary</h2>
          <p>Strong vector and graph match. Experience maps cleanly to LLM platform work, production MLOps, and mentorship expectations.</p>
          <p>Bias Guardian found no protected-class leakage in ranking rationale.</p>
        </section>
      </div>
    </div>
  );
}
