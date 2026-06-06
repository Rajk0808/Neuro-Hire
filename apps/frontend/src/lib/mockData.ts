import type { AgentEvent } from "@/types/agent";
import type { Candidate } from "@/types/candidate";
import type { Job } from "@/types/job";

export const jobs: Job[] = [
  {
    id: "ml-lead",
    title: "Senior ML Engineer",
    department: "Engineering",
    location: "Bengaluru, Remote",
    seniority: "senior",
    status: "open",
    salary_min: 4200000,
    salary_max: 6200000,
    currency: "INR",
    required_skills: ["Python", "LLMs", "Vector Search", "MLOps"],
    nice_to_have_skills: ["Graph DB", "Hiring SaaS"],
    dei_score: 98,
    applications_count: 284,
    shortlist_count: 18,
    created_at: "2026-05-29T10:00:00.000Z",
    updated_at: "2026-06-06T07:30:00.000Z",
    posted_urls: { linkedin: "#", naukri: "#" },
    hiring_manager_id: "hm-1"
  },
  {
    id: "product-designer",
    title: "Principal Product Designer",
    department: "Design",
    location: "Mumbai",
    seniority: "principal",
    status: "interviewing",
    salary_min: 3600000,
    salary_max: 5200000,
    currency: "INR",
    required_skills: ["Systems Thinking", "Figma", "Research"],
    nice_to_have_skills: ["AI UX", "Design Ops"],
    dei_score: 96,
    applications_count: 132,
    shortlist_count: 9,
    created_at: "2026-05-26T10:00:00.000Z",
    updated_at: "2026-06-06T08:00:00.000Z",
    posted_urls: { linkedin: "#" },
    hiring_manager_id: "hm-2"
  },
  {
    id: "strategy-analytics",
    title: "Strategy Analytics Lead",
    department: "Intelligence",
    location: "Hyderabad",
    seniority: "staff",
    status: "screening",
    salary_min: 3000000,
    salary_max: 4400000,
    currency: "INR",
    required_skills: ["SQL", "Market Intel", "Dashboards"],
    nice_to_have_skills: ["Compensation Modeling"],
    dei_score: 94,
    applications_count: 198,
    shortlist_count: 14,
    created_at: "2026-05-31T10:00:00.000Z",
    updated_at: "2026-06-06T08:15:00.000Z",
    posted_urls: { linkedin: "#" },
    hiring_manager_id: "hm-3"
  }
];

export const candidates: Candidate[] = [
  {
    id: "arjun-mehta",
    name: "Arjun Mehta",
    email: "arjun@example.com",
    location: "Pune",
    current_company: "Nexa Cloud",
    current_role: "Senior ML Platform Engineer",
    experience_years: 8,
    skills: ["Python", "RAG", "Kubernetes", "MLOps"],
    status: "shortlisted",
    retrieval_scores: { bm25: 91, vector: 96, graph: 88, rrf_score: 0.92 },
    bias_flag: false,
    resume_url: "#",
    linkedin_url: "#",
    applied_at: "2026-06-03T12:00:00.000Z",
    job_req_id: "ml-lead"
  },
  {
    id: "sana-iyer",
    name: "Sana Iyer",
    email: "sana@example.com",
    location: "Bengaluru",
    current_company: "Fabrica AI",
    current_role: "Applied AI Engineer",
    experience_years: 6,
    skills: ["LLMs", "Evaluation", "FastAPI", "Vector DB"],
    status: "interview_scheduled",
    retrieval_scores: { bm25: 87, vector: 93, graph: 84, rrf_score: 0.89 },
    bias_flag: false,
    resume_url: "#",
    linkedin_url: "#",
    applied_at: "2026-06-04T09:20:00.000Z",
    job_req_id: "ml-lead"
  },
  {
    id: "dev-patel",
    name: "Dev Patel",
    email: "dev@example.com",
    location: "Delhi",
    current_company: "SignalWorks",
    current_role: "Product Analytics Lead",
    experience_years: 9,
    skills: ["SQL", "Forecasting", "Compensation Intel"],
    status: "screened",
    retrieval_scores: { bm25: 84, vector: 86, graph: 92, rrf_score: 0.86 },
    bias_flag: false,
    resume_url: "#",
    applied_at: "2026-06-02T14:10:00.000Z",
    job_req_id: "strategy-analytics"
  }
];

export const agentEvents: AgentEvent[] = [
  { id: "a1", agent: "JD Architect", state: "active", message: "Rewriting role language for clarity and inclusion.", progress: 76, timestamp: "Just now" },
  { id: "a2", agent: "Resume Intelligence", state: "thinking", message: "Fusing vector, keyword, and graph retrieval scores.", progress: 64, timestamp: "2m ago" },
  { id: "a3", agent: "Interview Orchestrator", state: "active", message: "Holding three panel slots for shortlisted candidates.", progress: 82, timestamp: "5m ago" },
  { id: "a4", agent: "Market Intelligence", state: "idle", message: "Salary bands refreshed for Bengaluru and Hyderabad.", progress: 100, timestamp: "1h ago" }
];
