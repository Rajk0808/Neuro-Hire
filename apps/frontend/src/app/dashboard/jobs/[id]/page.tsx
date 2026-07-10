import { Badge } from "@/components/atoms/Badge";
import { CandidateCard } from "@/components/molecules/CandidateCard";
import { ScoreGauge } from "@/components/molecules/ScoreGauge";
import { candidateApi, JobApi } from "@/lib/api";
import { formatSalary } from "@/lib/utils";
import type { Candidate } from "@/types/candidate";

type JobDetailView = {
  id: string;
  title: string;
  status: string;
  department: string;
  location: string;
  salary_min: number;
  salary_max: number;
  currency: string;
  required_skills: string[];
  dei_score: number;
};

const createFallbackJob = (id: string, title = "Temporary Unavailable Job"): JobDetailView => ({
  id,
  title,
  status: "Offline",
  department: "Network Error",
  location: "Server Connection Refused",
  salary_min: 0,
  salary_max: 0,
  currency: "USD",
  required_skills: ["Backend Connection Error"],
  dei_score: 0
});

export default async function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  let job: JobDetailView | null = null;
  let candidatesList: Candidate[] = [];

  try {
    const jobData = (await JobApi.getJob(id)) as Partial<JobDetailView> | null;

    if (jobData && typeof jobData === "object") {
      job = {
        ...createFallbackJob(id, "Temporary Unavailable Job"),
        ...jobData,
        required_skills: Array.isArray(jobData.required_skills) ? jobData.required_skills : []
      };
    }

    const candidates = await candidateApi.Candidates(id);
    candidatesList = Array.isArray(candidates) ? candidates : [];
  } catch (error) {
    console.error("Backend server is offline! Using fallback data shape.", error);
    job = createFallbackJob(id);
    candidatesList = [];
  }

  if (!job) {
    job = {
      ...createFallbackJob(id, "Job Not Found"),
      status: "unknown",
      department: "Unknown",
      location: "Unknown",
      required_skills: []
    };
  }

  return (
    <div className="page-pad detail-page">
      <section className="panel detail-hero">
        <Badge label={job.status} />
        <h1>{job.title}</h1>
        <p>
          {job.department} · {job.location} · {formatSalary(job.salary_min, job.salary_max, job.currency)}
        </p>
        <div className="chip-row">
          {job.required_skills?.map((skill: string) => (
            <span key={skill}>{skill}</span>
          ))}
        </div>
      </section>
      
      <div className="dashboard-grid">
        <section className="panel" style={{ gridColumn: "span 4", padding: 24 }}>
          <ScoreGauge value={job.dei_score || 0} label="DEI Score" />
        </section>
        
        <section style={{ gridColumn: "span 8" }}>
          <div className="job-grid">
            {candidatesList
              .filter((candidate) => candidate.job_req_id === job.id)
              .map((candidate) => (
                <CandidateCard candidate={candidate} key={candidate.id} />
              ))}
          </div>
        </section>
      </div>
    </div>
  );
}
