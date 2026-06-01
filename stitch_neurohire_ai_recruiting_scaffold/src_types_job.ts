export type JobStatus = 'draft' | 'open' | 'screening' | 'interviewing' | 'closed'
export type Seniority = 'junior' | 'mid' | 'senior' | 'staff' | 'principal'

export interface Job {
  id: string
  title: string
  department: string
  location: string
  seniority: Seniority
  status: JobStatus
  salary_min: number
  salary_max: number
  currency: string
  required_skills: string[]
  nice_to_have_skills: string[]
  dei_score: number           // 0–100
  applications_count: number
  shortlist_count: number
  created_at: string
  updated_at: string
  posted_urls: Record<string, string>
  hiring_manager_id: string
}

export interface CreateJobDto {
  raw_input: string           // voice note transcript or text
  hiring_manager_id: string
}

export interface JobListResponse {
  items: Job[]
  total: number
  page: number
  limit: number
}
