import { useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useCandidateStore } from '@/store/candidateStore';
import { Candidate } from '@/types/candidate';

interface SearchParams {
  query: string;
  jobId?: string;
  status?: string;
}

export function useCandidateSearch(params: SearchParams) {
  const { setCandidates, setLoading, setError } = useCandidateStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['candidates', params],
    queryFn: async () => {
      try {
        const response = await api.get<{ items: Candidate[] }>('/candidates/search', {
          params,
        });
        return response.data.items;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to search candidates');
        throw err;
      }
    },
    enabled: !!params.query,
  });

  const handleSearch = useCallback((results: Candidate[]) => {
    setCandidates(results);
    setLoading(false);
  }, [setCandidates, setLoading]);

  return {
    candidates: data || [],
    isLoading,
    error: error instanceof Error ? error.message : null,
    handleSearch,
  };
}
