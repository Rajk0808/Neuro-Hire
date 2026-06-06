import { CandidateCard } from "@/components/molecules/CandidateCard";
import { ShortlistTable } from "@/components/organisms/ShortlistTable";
import { candidates } from "@/lib/mockData";

export default function CandidatesPage() {
  return (
    <div className="page-pad">
      <div className="section-head">
        <div>
          <span>Talent graph</span>
          <h1>Candidate Shortlist</h1>
        </div>
      </div>
      <div className="job-grid">{candidates.map((candidate) => <CandidateCard candidate={candidate} key={candidate.id} />)}</div>
      <ShortlistTable />
    </div>
  );
}
