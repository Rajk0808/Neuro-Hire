import { create } from "zustand";
import { jobs } from "@/lib/mockData";
import type { Job } from "@/types/job";

type JobStore = {
  jobs: Job[];
  selectJob: (id: string) => Job | undefined;
};

export const useJobStore = create<JobStore>(() => ({
  jobs,
  selectJob: (id) => jobs.find((job) => job.id === id)
}));
