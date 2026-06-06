export type CandidateStatus =
  | "applied"
  | "screened"
  | "shortlisted"
  | "interview_scheduled"
  | "interviewing"
  | "offer_sent"
  | "hired"
  | "rejected";

export interface RetrievalScores {
  bm25: number;
  vector: number;
  graph: number;
  rrf_score: number;
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  location: string;
  current_company: string;
  current_role: string;
  experience_years: number;
  skills: string[];
  status: CandidateStatus;
  retrieval_scores: RetrievalScores;
  bias_flag: boolean;
  resume_url: string;
  linkedin_url?: string;
  applied_at: string;
  job_req_id: string;
}
