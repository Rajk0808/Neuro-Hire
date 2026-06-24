from pydantic import BaseModel, Field

class GetCandidates(BaseModel):
    job_id: int = Field(..., description="The ID of the job for which to retrieve candidates.")