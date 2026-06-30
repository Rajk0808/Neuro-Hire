from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi import BackgroundTasks, HTTPException
from services.jwt_service import verify_jwt_token
from services.pg_db_service import execute_query
from schemas.jobs import JobCreateRequest, DeiScoreRequest
from agents.jd_arcitecture_agent import *
from schemas.jobs import JobRequest, HumanFeedbackRequest
from agents.jd_arcitecture_agent.asyncrun import generate_or_edit_jd, publish_approved_jd, db_sessions
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

@router.post("/jobs/start")
async def start_pipeline(request: JobRequest, background_tasks: BackgroundTasks):
    """Endpoint 1: Instantly registers a user request and runs the crew in the background."""
    session_id = request.session_id
    
    # Initialize isolated session state
    db_sessions[session_id] = {
        "status": "queued",
        "raw_input": request.raw_input,
        "current_draft": None
    }
    
    # Offload the heavy CrewAI execution to background workers so the API responds immediately
    background_tasks.add_task(generate_or_edit_jd, session_id, request.raw_input)
    return {"message": "Pipeline initiated", "session_id": session_id, "status": "processing"}


@router.get("/jobs/status/{session_id}")
async def get_status(session_id: str):
    """Endpoint 2: Allows web UIs to poll and fetch the generated draft text."""
    if session_id not in db_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions[session_id]


@router.post("/jobs/review")
async def submit_human_review(request: HumanFeedbackRequest, background_tasks: BackgroundTasks):
    """Endpoint 3: The non-blocking HITL gateway. Accepts feedback or approvals."""
    session_id = request.session_id
    
    if session_id not in db_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session_data = db_sessions[session_id]
    
    if request.approved:
        # Branch A: Human says CONTINUE TO POST
        background_tasks.add_task(publish_approved_jd, session_id, session_data["current_draft"])
        return {"message": "Approval received. Job is being posted.", "status": "posting"}
    else:
        # Branch B: Human says RETRY WITH FEEDBACK
        new_prompt = f"Original Criteria: {session_data['raw_input']}\n\nApply this feedback: {request.feedback}"
        background_tasks.add_task(generate_or_edit_jd, session_id, new_prompt)
        return {"message": "Feedback received. Regenerating draft...", "status": "processing"}
