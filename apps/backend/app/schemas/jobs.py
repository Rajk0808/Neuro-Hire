from pydantic import BaseModel
from typing import Literal, Optional

class JobCreateRequest(BaseModel):
    user_id: str
    description_query: str 

class DeiScoreRequest(BaseModel):
    description: str       

class JobStatus(BaseModel):
    status: str = Literal["draft", "open", "screening", "interviewing", "closed"]

class JobSeniority(BaseModel):
    seniority: str = Literal["junior", "mid", "senior", "staff", "principal"]

class JobResponse(BaseModel):
  id: str
  title: str
  department: str
  location: str
  seniority: JobSeniority
  status: JobStatus
  salary_min: int
  salary_max: int
  currency: str
  required_skills: list[str]
  nice_to_have_skills: list[str]
  dei_score: int
  applications_count: int
  shortlist_count: int
  created_at: str
  updated_at: str
  posted_urls: dict[str, str]
  hiring_manager_id: str

class JobRequest(BaseModel):
    session_id: str
    raw_input: str

class HumanFeedbackRequest(BaseModel):
    session_id: str
    feedback: Optional[str] = None
    approved: bool 
