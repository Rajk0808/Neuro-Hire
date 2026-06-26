import { JobStatus, Seniority, Job as JobResponse } from "@/types/job";
import { Candidate as CandidateResponse } from "@/types/candidate";
import axios, { isAxiosError } from "axios";

const normalizeApiBaseUrl = (url: string) =>
  url.trim().replace(/\/+$/, "").replace(/\/v1$/, "");

export const API_BASE_URL = normalizeApiBaseUrl(
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"
);

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true // Crucial: This silently passes the access_token cookie
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

// ==========================================
// TYPES DEFINITIONS
// ==========================================
type JobCreateResponse = {
  id: string;
  generated_text: string;
  status: string;
};


type Candidate = {
  id: string;
  name: string;
  email: string;
  phone: string;
  skills: string[];
  experience_years: number;
  applied_at: string;
};

type AuthResponse = {
  message: string;
  token: string;
};

type RegisterPayload = {
  companyName: string;
  email: string;
  password: string;
};

type LoginPayload = {
  email: string;
  password: string;
};

type ApiErrorPayload = {
  detail?: string;
  message?: string;
};

// ==========================================
// API IMPLEMENTATIONS
// ==========================================
const postAuthForm = async <TResponse>(path: string, formData: FormData) => {
  const response = await api.post<TResponse>(path, formData); 
  return response;
};

export const loginRecruiter = ({ email, password }: LoginPayload) => {
  const formData = new FormData();
  formData.append("email", email);
  formData.append("password", password);
  return postAuthForm<AuthResponse>("/v1/login", formData); 
};

export const registerRecruiter = ({ companyName, email, password }: RegisterPayload) => {
  const formData = new FormData();
  formData.append("company_name", companyName);
  formData.append("email", email);
  formData.append("password", password);

  return postAuthForm<AuthResponse>("/v1/register", formData);
};

export const candidateApi = {
  createCandidate: (candidateData: Omit<Candidate, "id" | "applied_at">) => {
    return api.post("/v1/create-candidate", candidateData);
  },
  getCandidate: (candidateId: string) => {
    return api.get(`/v1/get_candidate/${candidateId}`);
  },
  Candidates: (jobReqId: string) => {
    return api.get(`/v1/candidates/${jobReqId}`);
  }
};

export const JobApi = {
  // 1. Fetch all jobs (Matches @router.get("/jobs"))
  getJobs: () => {
    return api.get<{ jobs: JobResponse[] }>("/v1/jobs").then((response) => response.data);
  },
  
  createJob: (request: { jd_query: string }) => {
    return api.post<JobCreateResponse>("/v1/create-job", { 
      description_query: request.jd_query 
    });
  },
  
  // 2. FIXED: Path updated to "/v1/jobs/dei-score" and body key updated to "description"
  getDEIScore: (jobDescription: string) => {
    return api.post<{ dei_score: number }>("/v1/jobs/dei-score", { 
      description: jobDescription 
    });
  },
  
  getJob: (jobId: string) => {
    return api.get(`/v1/jobs/${jobId}`).then((response) => response.data);
  }
};  

export const DashboardApi = {
  getOpenRoles: () => {
    return api.get<{ open_roles: number }>("/v1/dashboard/open-roles").then((response) => response.data);
  },
  getCandidatesCountThisWeek: () => {
    return api.get<{ candidates_count: number }>("/v1/dashboard/candidates-count-current-week").then((response) => response.data);
  },
  getAverageTimeToHire: () => {
    return api.get<{ average_time_to_hire: number }>("/v1/dashboard/average-time-to-hire").then((response) => response.data);
  },
  getDEIScoreAverage: () => {
    return api.get<{ average_dei_score: number }>("/v1/dashboard/average-dei-score").then((response) => response.data);
  },
  getRecentJobs: () => {
    return api.get<{}>("/v1/dashboard/recent-jobs").then((response) => response.data);
  },

  getRecentRecruiterActivities: () => {
    return api.get<{}>("/v1/dashboard/recent-recruiter-activities").then((response) => response.data);
  }
};  
export const getApiErrorMessage = (error: unknown, fallback: string) => {
  if (isAxiosError<ApiErrorPayload>(error)) {
    const detail = error.response?.data?.detail;

    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg ?? "Validation error").join(", ");
    }

    if (detail || error.response?.data?.message) {
      return detail ?? error.response?.data?.message ?? fallback;
    }

    if (!error.response) {
      return `${fallback} Tried ${API_BASE_URL}.`;
    }

    return error.message;
  }

  return error instanceof Error ? error.message : fallback;
};

export default api;
