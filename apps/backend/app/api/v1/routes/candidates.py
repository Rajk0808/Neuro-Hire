import logging
from typing import List
from apps.backend.app.services.jwt_service import verify_jwt_token
from services.pg_db_service import execute_query
from fastapi import APIRouter, Depends
from schemas.candidates import GetCandidates

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/candidates")
async def get_candidates(request: GetCandidates, current_user = Depends(verify_jwt_token)):
    res = execute_query("SELECT * FROM candidates WHERE job_req_id = %s", (request.job_id,))
    logger.info(f"Retrieved candidates for job_req_id {request.job_id}: {res}")
    return {"candidates": []}

@router.post("/create-candidate")
async def create_candidate(candidates: List[dict], current_user = Depends(verify_jwt_token)):
    # Logic to create new candidates in the database
    return {"message": "Candidates created successfully"}

@router.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: int, current_user = Depends(verify_jwt_token)):
    # Logic to retrieve a specific candidate by ID from the database
    return {"candidate": {"id": candidate_id}}

@router.put("/candidates/{candidate_id}")
async def update_candidate(candidate_id: int, candidate: dict, current_user = Depends(verify_jwt_token)):
    # Logic to update a specific candidate by ID in the database
    return {"message": "Candidate updated successfully"}

@router.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: int, current_user = Depends(verify_jwt_token)):
    # Logic to delete a specific candidate by ID from the database
    return {"message": "Candidate deleted successfully"}


