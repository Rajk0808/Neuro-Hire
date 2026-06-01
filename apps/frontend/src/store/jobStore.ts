import { create } from 'zustand';
import { Job, JobListResponse } from '@/types/job';

interface JobStore {
  jobs: Job[];
  selectedJob: Job | null;
  isLoading: boolean;
  error: string | null;
  pagination: { page: number; limit: number; total: number };
  setJobs: (jobs: Job[]) => void;
  setSelectedJob: (job: Job | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPagination: (page: number, limit: number, total: number) => void;
  addJob: (job: Job) => void;
  updateJob: (id: string, updates: Partial<Job>) => void;
  removeJob: (id: string) => void;
  reset: () => void;
}

export const useJobStore = create<JobStore>((set) => ({
  jobs: [],
  selectedJob: null,
  isLoading: false,
  error: null,
  pagination: { page: 1, limit: 10, total: 0 },
  setJobs: (jobs) => set({ jobs }),
  setSelectedJob: (selectedJob) => set({ selectedJob }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setPagination: (page, limit, total) =>
    set({ pagination: { page, limit, total } }),
  addJob: (job) => set((state) => ({ jobs: [job, ...state.jobs] })),
  updateJob: (id, updates) =>
    set((state) => ({
      jobs: state.jobs.map((job) => (job.id === id ? { ...job, ...updates } : job)),
      selectedJob: state.selectedJob?.id === id ? { ...state.selectedJob, ...updates } : state.selectedJob,
    })),
  removeJob: (id) =>
    set((state) => ({
      jobs: state.jobs.filter((job) => job.id !== id),
    })),
  reset: () =>
    set({
      jobs: [],
      selectedJob: null,
      isLoading: false,
      error: null,
      pagination: { page: 1, limit: 10, total: 0 },
    }),
}));
