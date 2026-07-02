from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from uuid import uuid4
from services.jwt_service import verify_jwt_token
from services.pg_db_service import execute_query
from schemas.jobs import JobCreateRequest, DeiScoreRequest
from agents.jd_arcitecture_agent import *
from schemas.jobs import JobRequest, HumanFeedbackRequest
from agents.jd_arcitecture_agent.asyncrun import generate_or_edit_jd, publish_approved_jd
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/jobs")
async def get_jobs(current_user = Depends(verify_jwt_token)):
    res = await execute_query("SELECT * FROM jobs WHERE recruiter_email = %s ORDER BY created_at DESC", (current_user["useremail"],))
    logger.info(f"Retrieved jobs: {res}")
    return {"jobs": res}

@router.post("/create-job")
async def create_job(request: JobCreateRequest, background_tasks: BackgroundTasks, current_user = Depends(verify_jwt_token)):
    return await start_pipeline(
        JobRequest(
            session_id=None,
            raw_input=request.description_query,
            user_id=await get_user_id_by_email(current_user["useremail"]),
        ),
        background_tasks,
    )

@router.get('/jobs/dei-score')
async def get_jobs_by_dei_score(request: DeiScoreRequest, current_user = Depends(verify_jwt_token)):
    dei_tool = DEILanguageTool()
    res = dei_tool._run(request.description)
    return {"dei_score": res}


async def get_user_id_by_email(email: str) -> int:
    user_rows = await execute_query("SELECT id FROM users WHERE email = %s", (email,))
    if not user_rows:
        raise HTTPException(status_code=404, detail="User not found")
    return user_rows[0]["id"]


async def start_pipeline(request: JobRequest, background_tasks: BackgroundTasks):
    """Endpoint 1: Instantly registers a user request and runs the crew in the background."""
    user_id = request.user_id
    if user_id is None:
        raise HTTPException(status_code=400, detail="User id is required to start a session")

    session_id = str(uuid4())
    await execute_query(
        "INSERT INTO sessions (id, user_id, status, raw_draft) VALUES (%s, %s, %s, %s)",
        (session_id, user_id, "queued", request.raw_input),
    )
    
    # Offload the heavy CrewAI execution to background workers so the API responds immediately
    background_tasks.add_task(generate_or_edit_jd, session_id, request.raw_input)
    return {"message": "Pipeline initiated", "session_id": session_id, "status": "processing"}


@router.get("/jobs/status/{session_id}")
async def get_status(session_id: str):
    """Endpoint 2: Allows web UIs to poll and fetch the generated draft text."""
    session_data = await execute_query("SELECT * FROM sessions WHERE id = %s", (session_id,))
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_data[0]


@router.post("/jobs/review")
async def submit_human_review(request: HumanFeedbackRequest, background_tasks: BackgroundTasks):
    """Endpoint 3: The non-blocking HITL gateway. Accepts feedback or approvals."""
    session_id = request.session_id
    
    session_data = await execute_query("SELECT * FROM sessions WHERE id = %s", (session_id,))
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session_data = session_data[0]
    action = request.action or ("continue" if request.approved else "retry")

    if action == "stop":
        await execute_query("UPDATE sessions SET status = 'stopped' WHERE id = %s", (session_id,))
        return {"message": "Session stopped. The current draft has been held.", "status": "stopped"}

    if action == "continue" or request.approved:
        # Branch A: Human says CONTINUE TO POST
        background_tasks.add_task(
            publish_approved_jd,
            session_id,
            session_data.get("current_draft") or session_data.get("raw_draft") or "",
            request.selected_channels or [],
        )
        return {"message": "Approval received. Job is being posted.", "status": "posting"}
    else:
        # Branch B: Human says RETRY WITH FEEDBACK
        new_prompt = f"Original Criteria: {session_data.get('raw_draft') or session_data.get('raw_input') or ''}\n\nApply this feedback: {request.feedback or ''}"
        background_tasks.add_task(generate_or_edit_jd, session_id, new_prompt)
        return {"message": "Feedback received. Regenerating draft...", "status": "processing"}
