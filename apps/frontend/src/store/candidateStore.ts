import { create } from "zustand";
import { candidates } from "@/lib/mockData";
import type { Candidate } from "@/types/candidate";

type CandidateStore = {
  candidates: Candidate[];
  selectCandidate: (id: string) => Candidate | undefined;
};

export const useCandidateStore = create<CandidateStore>(() => ({
  candidates,
  selectCandidate: (id) => candidates.find((candidate) => candidate.id === id)
}));
