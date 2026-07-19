from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi import WebSocket, WebSocketDisconnect
from uuid import uuid4
from services.jwt_service import verify_jwt_token
from services.pg_db_service import execute_query
from schemas.jobs import DeiScoreRequest
from agents.jd_arcitecture_agent import *
from fastapi.concurrency import run_in_threadpool
from fastapi import Query
from schemas.jobs import JobRequest, HumanFeedbackRequest
from agents.jd_arcitecture_agent.schema.research_schema import DEILanguageArgs
from agents.jd_arcitecture_agent.asyncrun import generate_or_edit_jd, publish_approved_jd
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/jobs")
async def get_jobs(current_user = Depends(verify_jwt_token)):
    res = await execute_query("SELECT * FROM jobs WHERE recruiter_email = $1 ORDER BY created_at DESC", (current_user["useremail"],))
    logger.info(f"Retrieved jobs: {res}")
    return {"jobs": res}

@router.websocket("/jobs/create-job/ws")
async def create_job_ws(websocket: WebSocket):
    # 1. Accept the connection immediately (Authentication was handled by your middleware)
    await websocket.accept()
    
    # Retrieve user details attached by your middleware (adjust property name if needed)
    current_user = getattr(websocket.state, "user", {"useremail": "unknown_user"})
    logger.info(f"WebSocket connection accepted for user: {current_user['useremail']}")
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if "description_query" not in data:
                await websocket.send_json({"error": "Missing 'description_query' in request"})
                continue

            description_query = data["description_query"]
            session_id = str(uuid4())

            # Send initial processing state to frontend
            await websocket.send_json({
                "message": "Pipeline initiated", 
                "session_id": session_id, 
                "status": "processing",
                "result": "Pipeline started. Generating draft..."
            })

            res = await generate_or_edit_jd(session_id, description_query)
            # Send final completed state
            await websocket.send_json({
                "message": "Success", 
                "session_id": session_id, 
                "status": "completed", 
                "result": res.raw if hasattr(res, 'raw') else res
            })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {current_user['useremail']}")
    except Exception as e:
        logger.error(f"Error in WebSocket execution: {str(e)}")
        try:
            await websocket.send_json({"error": "Internal server error"})
        except:
            pass


@router.post('/jobs/dei-score')
async def get_jobs_by_dei_score(request: DeiScoreRequest):
    dei_tool = DEILanguageTool()
    res = await dei_tool._arunc(args=DEILanguageArgs(job_description=request.description, threshold=0.5))
    return {"dei_score": res}


async def get_user_id_by_email(email: str) -> int:
    user_rows = await execute_query("SELECT id FROM users WHERE email = $1", (email,))
    if not user_rows:
        raise HTTPException(status_code=404, detail="User not found")
    return user_rows[0]["id"]


async def start_pipeline(request: JobRequest, background_tasks: BackgroundTasks):
    """Endpoint 1: Instantly registers a user request and runs the crew in the background."""
    user_id = request.user_id
    if user_id is None:
        raise HTTPException(status_code=400, detail="User id is required to start a session")

    res = await execute_query(
        "INSERT INTO sessions (user_id, status, raw_draft) VALUES ($1, 'queued', $2)",
        (user_id, request.raw_input)
    )
    session_id = res.get("id") 
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
