from fastapi import APIRouter, Depends
from services.jwt_service import verify_jwt_token
from services.pg_db_service import execute_query
from schemas.jobs import JobCreateRequest, DeiScoreRequest
from agents.JD_Arcitecture_agent.tools.dei_language_auditor_tool import DEILanguageTool
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/jobs")
async def get_jobs(current_user = Depends(verify_jwt_token)):
    res = execute_query(f"SELECT * FROM jobs WHERE recruiter_email = '{current_user.email}' ORDER BY created_at DESC")
    logger.info(f"Retrieved jobs: {res}")
    return {"jobs": res}

@router.post("/create-job")
async def create_job(request: JobCreateRequest, current_user = Depends(verify_jwt_token)):
    return {"message": "Job created successfully"}

@router.get('/jobs/dei-score')
async def get_jobs_by_dei_score(request: DeiScoreRequest, current_user = Depends(verify_jwt_token)):
    dei_tool = DEILanguageTool()
    res = dei_tool._run(request.description)
    return {"dei_score": res}