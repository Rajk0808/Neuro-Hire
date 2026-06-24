import { notFound } from "next/navigation";
import { Badge } from "@/components/atoms/Badge";
import { CandidateCard } from "@/components/molecules/CandidateCard";
import { ScoreGauge } from "@/components/molecules/ScoreGauge";
import { candidateApi, JobApi} from "@/lib/api";
import { formatSalary } from "@/lib/utils";

export default async function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const job = await JobApi.getJob(id);
  if (!job) notFound();

  return (
    <div className="page-pad detail-page">
      <section className="panel detail-hero">
        <Badge label={job.status} />
        <h1>{job.title}</h1>
        <p>{job.department} · {job.location} · {formatSalary(job.salary_min, job.salary_max, job.currency)}</p>
        <div className="chip-row">{job.required_skills.map((skill) => <span key={skill}>{skill}</span>)}</div>
      </section>
      <div className="dashboard-grid">
        <section className="panel" style={{ gridColumn: "span 4", padding: 24 }}>
          <ScoreGauge value={job.dei_score} label="DEI Score" />
        </section>
        <section style={{ gridColumn: "span 8" }}>
          <div className="job-grid">
            {candidates.filter((candidate) => candidate.job_req_id === job.id).map((candidate) => <CandidateCard candidate={candidate} key={candidate.id} />)}
          </div>
        </section>
      </div>
    </div>
  );
}
