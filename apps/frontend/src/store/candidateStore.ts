import { create } from 'zustand';
import { Candidate } from '@/types/candidate';

interface CandidateStore {
  candidates: Candidate[];
  selectedCandidate: Candidate | null;
  isLoading: boolean;
  error: string | null;
  pagination: { page: number; limit: number; total: number };
  setCandidates: (candidates: Candidate[]) => void;
  setSelectedCandidate: (candidate: Candidate | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPagination: (page: number, limit: number, total: number) => void;
  addCandidate: (candidate: Candidate) => void;
  updateCandidate: (id: string, updates: Partial<Candidate>) => void;
  removeCandidate: (id: string) => void;
  reset: () => void;
}

export const useCandidateStore = create<CandidateStore>((set) => ({
  candidates: [],
  selectedCandidate: null,
  isLoading: false,
  error: null,
  pagination: { page: 1, limit: 10, total: 0 },
  setCandidates: (candidates) => set({ candidates }),
  setSelectedCandidate: (selectedCandidate) => set({ selectedCandidate }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setPagination: (page, limit, total) =>
    set({ pagination: { page, limit, total } }),
  addCandidate: (candidate) =>
    set((state) => ({ candidates: [candidate, ...state.candidates] })),
  updateCandidate: (id, updates) =>
    set((state) => ({
      candidates: state.candidates.map((candidate) =>
        candidate.id === id ? { ...candidate, ...updates } : candidate
      ),
      selectedCandidate: state.selectedCandidate?.id === id 
        ? { ...state.selectedCandidate, ...updates } 
        : state.selectedCandidate,
    })),
  removeCandidate: (id) =>
    set((state) => ({
      candidates: state.candidates.filter((candidate) => candidate.id !== id),
    })),
  reset: () =>
    set({
      candidates: [],
      selectedCandidate: null,
      isLoading: false,
      error: null,
      pagination: { page: 1, limit: 10, total: 0 },
    }),
}));
