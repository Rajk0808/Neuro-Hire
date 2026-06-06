import { Badge } from "@/components/atoms/Badge";
import { ScoreBar } from "@/components/atoms/ScoreBar";
import { candidates } from "@/lib/mockData";

export function ShortlistTable() {
  return (
    <div className="panel table-panel">
      <div className="section-head">
        <div>
          <span>Shortlist</span>
          <h2>Ranked Candidates</h2>
        </div>
      </div>
      <div className="nh-table">
        {candidates.map((candidate) => (
          <a href={`/dashboard/candidates/${candidate.id}`} className="nh-row" key={candidate.id}>
            <strong>{candidate.name}</strong>
            <span>{candidate.current_role}</span>
            <span>{candidate.location}</span>
            <Badge label={candidate.status} />
            <ScoreBar value={Math.round(candidate.retrieval_scores.rrf_score * 100)} />
          </a>
        ))}
      </div>
    </div>
  );
}
