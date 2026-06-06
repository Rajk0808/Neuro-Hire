"use client";

import { jobs } from "@/lib/mockData";

export function useJobPipeline() {
  return {
    jobs,
    open: jobs.filter((job) => job.status === "open"),
    interviewing: jobs.filter((job) => job.status === "interviewing"),
    screening: jobs.filter((job) => job.status === "screening")
  };
}
