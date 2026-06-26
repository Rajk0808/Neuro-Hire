"use client"; // 👈 Add this exact string at the very top of the file

import { JobCard } from "@/components/molecules/JobCard";
import { DashboardApi } from "@/lib/api";
import { Job } from "@/types/job";
import { useState, useEffect } from "react";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    async function fetchJobs() {
      try {
        const recentJobsData = await DashboardApi.getRecentJobs();
        setJobs(Array.isArray(recentJobsData) ? recentJobsData : []);
      } catch (error) {
        console.error("Failed to fetch recent jobs", error);
      }
    }

    fetchJobs();
  }, []);

  return (
    <div className="page-pad">
      <div className="section-head">
        <div>
          <span>Requisitions</span>
          <h1>Job Listings</h1>
        </div>
        <a className="nh-button nh-button-primary" href="/dashboard/jobs/new">New job</a>
      </div>
      <div className="job-grid">
        {jobs.map((job) => (
          <JobCard job={job} key={job.id} />
        ))}
      </div>
    </div>
  );
}
