from pydantic import BaseModel, Field

class JobCreateRequest(BaseModel):
    description_query: str 

class DeiScoreRequest(BaseModel):
    description: str       