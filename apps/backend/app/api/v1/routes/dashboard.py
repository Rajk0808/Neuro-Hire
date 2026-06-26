from fastapi import APIRouter, Request, Response, HTTPException, status, Depends, Form
from db.session import get_pg_connection
from services.pg_db_service import execute_query
from services.jwt_service import verify_jwt_token
from schemas.candidates import Candidate
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard/open-roles")
async def get_open_roles(response: Response, current_user: dict = Depends(verify_jwt_token)):
    pg_connection = await get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database connection failed"
        )
    try:
        result = await execute_query("SELECT COUNT(*) FROM roles r WHERE r.status = 'open' AND r.recruiter_email = $1", (current_user.get("user_id"),))
        open_roles_count = result[0][0] if result else 0
        return {"open_roles": open_roles_count}
    except Exception as e:
        logger.error(f"Error fetching open roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching open roles"
        )
@router.get("/dashboard/candidates-count-current-week")
async def get_candidates_count_current_week(request: Request, response: Response, current_user: dict = Depends(verify_jwt_token)):
    pg_connection = await get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database connection failed"
        )
    try:
        result = await execute_query(
            "SELECT COUNT(*) FROM candidates c WHERE c.created_at >= NOW() - INTERVAL '7 days' AND c.recruiter_email = $1", 
            (current_user.get("useremail"),)
        )
        candidates_count = result[0][0] if result else 0
        return {"data": candidates_count}
    except Exception as e:
        logger.error(f"Error fetching candidates count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching candidates count"
        )

@router.get('/dashboard/average-time-to-hire')
async def get_average_time_to_hire(request: Request, response: Response, current_user: dict = Depends(verify_jwt_token)):
    pg_connection = await get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database connection failed"
        )
    try:
        result = await execute_query(
            "SELECT AVG(EXTRACT(EPOCH FROM (c.hired_at - c.created_at))) / 3600 AS average_time_to_hire_hours "
            "FROM candidates c "
            "WHERE c.hired_at IS NOT NULL AND c.recruiter_email = $1", 
            (current_user.get("useremail"),)
        )
        average_time_to_hire = result[0][0] if result and result[0][0] is not None else 0
        return {"data": average_time_to_hire}
    except Exception as e:
        logger.error(f"Error fetching average time to hire: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching average time to hire"
        )

@router.get('/dashboard/average-dei-score')
async def getDEIaverage(response: Response, current_user: dict = Depends(verify_jwt_token)):
    pg_connection = await get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database connection failed"
        )
    try:
        result = await execute_query(
            "SELECT AVG(c.dei_score) AS average_dei_score "
            "FROM candidates c "
            "WHERE c.recruiter_email = $1", 
            (current_user.get("useremail"),)
        )
        average_dei_score = result[0][0] if result and result[0][0] is not None else 0
        return {"data": average_dei_score}
    except Exception as e:
        logger.error(f"Error fetching average DEI score: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching average DEI score"
        )

@router.get('/dashboard/recent-jobs')
async def get_recent_jobs(response: Response, current_user: dict = Depends(verify_jwt_token)):
    pg_connection = await get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    try:
        result = await execute_query(
            "SELECT j.id as id, j.title as title, j.department as department, j.location as location, j.required_skills as required_skills, j.salary_min as salary_min, j.salary_max as salary_max, j.dei_score as dei_score, j.status as status FROM jobs JOIN users u ON j.hiring_manager_id = u.id WHERE u.email = $1 ORDER BY j.created_at DESC LIMIT 5",
            (current_user.get("useremail"),)
        )
        return {"data": result}
    except Exception as e:
        logger.error(f"Error fetching recent jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching recent jobs"
        )

@router.get('/dashboard/recent-recruiter-activities')
async def get_recent_recruiter_activities(response: Response, current_user: dict = Depends(verify_jwt_token)):
    pg_connection = await get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    try:
        result = await execute_query(
            "SELECT c.name as name, c.current_role as current_role, c.location as location, c.status as status, c.rrf_score as rrf_score FROM candidates c JOIN jobs_applications ja ON c.id = ja.candidate_id JOIN jobs j ON ja.job_id = j.id JOIN users u ON j.hiring_manager_id = u.id WHERE u.email = $1",
            (current_user.get("useremail"),)
        )
        return {"data": result}
    except Exception as e:
        logger.error(f"Error fetching recent recruiter activities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching recent recruiter activities"
        )