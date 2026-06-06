import { JobCard } from "@/components/molecules/JobCard";
import { jobs } from "@/lib/mockData";

export default function JobsPage() {
  return (
    <div className="page-pad">
      <div className="section-head">
        <div>
          <span>Requisitions</span>
          <h1>Job Listings</h1>
        </div>
        <a className="nh-button nh-button-primary" href="/dashboard/jobs/new">New job</a>
      </div>
      <div className="job-grid">{jobs.map((job) => <JobCard job={job} key={job.id} />)}</div>
    </div>
  );
}
