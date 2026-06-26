import { Badge } from "@/components/atoms/Badge";
import { CandidateCard } from "@/components/molecules/CandidateCard";
import { ScoreGauge } from "@/components/molecules/ScoreGauge";
import { candidateApi, JobApi } from "@/lib/api";
import { formatSalary } from "@/lib/utils";

export default async function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  
  // 1. Initialize safe default structures
  let job: any = null;
  let candidatesList: any[] = [];

  try {
    // 2. Attempt to fetch data from the backend
    job = await JobApi.getJob(id);
    const candidates = await candidateApi.Candidates(id);
    candidatesList = Array.isArray(candidates) ? candidates : [];
  } catch (error) {
    // 3. If ECONNREFUSED or any network error happens, catch it here
    console.error("Backend server is offline! Using fallback data shape.", error);
    
    // Set fallback object instead of an empty array so page properties don't crash
    job = {
      id: id,
      title: "Temporary Unavailable Job",
      status: "Offline",
      department: "Network Error",
      location: "Server Connection Refused",
      salary_min: 0,
      salary_max: 0,
      currency: "USD",
      required_skills: ["Backend Connection Error"],
      dei_score: 0
    };
    candidatesList = [];
  }

  // Double check in case API resolved but returned null
  if (!job) {
    job = { title: "Job Not Found", required_skills: [] };
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
