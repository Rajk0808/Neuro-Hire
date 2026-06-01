import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useJobStore } from '@/store/jobStore';
import { Job, JobListResponse } from '@/types/job';

interface PipelineParams {
  page?: number;
  limit?: number;
  status?: string;
}

export function useJobPipeline(params?: PipelineParams) {
  const { setJobs, setPagination, setLoading, setError } = useJobStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['jobs-pipeline', params],
    queryFn: async () => {
      try {
        const response = await api.get<JobListResponse>('/jobs', { params });
        const { items, total, page, limit } = response.data;
        
        setJobs(items);
        setPagination(page, limit, total);
        setLoading(false);

        return response.data;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch jobs');
        throw err;
      }
    },
  });

  return {
    jobs: data?.items || [],
    total: data?.total || 0,
    page: data?.page || 1,
    limit: data?.limit || 10,
    isLoading,
    error: error instanceof Error ? error.message : null,
  };
}
