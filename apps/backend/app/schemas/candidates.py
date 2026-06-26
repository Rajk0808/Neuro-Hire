from pydantic import BaseModel, Field
from typing import Literal
class GetCandidates(BaseModel):
    job_id: int = Field(..., description="The ID of the job for which to retrieve candidates.")

class CandidateStatus(BaseModel):
    value: Literal["applied", "screened", "shortlisted", "rejected", "hired", "interview_scheduled", "interview_completed", "interviewing", "offer_sent"] = Field(..., description="The status of the candidate.")

class RetrievalScores(BaseModel):
    bm25: float = Field(..., description="The BM25 score for the candidate.")                               
    vector: float = Field(..., description="The vector similarity score for the candidate.")
    graph: float = Field(..., description="The graph-based score for the candidate.")
    rrf_score: float = Field(..., description="The Reciprocal Rank Fusion (RRF) score for the candidate.")

class Candidate(BaseModel):
    id: str
    name: str
    email: str
    location: str
    current_company: str
    current_role: str
    experience_years: int
    skills: list[str]
    status: CandidateStatus
    retrieval_scores: RetrievalScores
    bias_flag: bool
    resume_url: str
    linkedin_url: str | None
    applied_at: str
    job_req_id: str