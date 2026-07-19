import os
from fastapi import APIRouter, Response, HTTPException, status, Form
from db.postgres import get_pg_connection
from services.pg_db_service import execute_query
from services.jwt_service import create_jwt_token
from argon2 import PasswordHasher, exceptions as argon2_exceptions
import logging
router = APIRouter()
logger = logging.getLogger(__name__)
ph = PasswordHasher()

RECRUITER_SCOPES = [
    "user:read",
    "user:write",
    "job:read",
    "job:write",
    "candidate:read",
    "candidate:write",
    "analytics:read",
]

@router.post("/login")
async def login(email: str = Form(...), password: str = Form(...), response: Response = None):
    pg_connection = await get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database connection failed"
        )
    await pg_connection.close()

    user = await execute_query("SELECT email, password_hash FROM users WHERE email = $1", (email,))
    if not user:
        logger.error("Invalid login credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    userpassword = user[0]["password_hash"]
    logging.info("User found, verifying password for email: %s", email)
    try:
        res = ph.verify(userpassword, password)
    except argon2_exceptions.VerifyMismatchError:
        res = False
    if not res:
        logger.error("Invalid login credentials for email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    token = await create_jwt_token({"sub": email, "scopes": RECRUITER_SCOPES}, None)
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,        # Prevents client-side JS (.tsx) from reading the cookie
        max_age=1800,         # Expiration time in seconds (30 mins)
        expires=1800,
        samesite="lax",       # Protects against CSRF attacks
        secure=False,         # Set to True in production (requires HTTPS)
    )
    return {"message": "Login successful", "token": token}


@router.post("/register")
async def register(
    company_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),  
    response: Response = None
):
    pg_connection = await get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    await pg_connection.close()

    # Check for existing user collision
    existing_user = await execute_query("SELECT * FROM users WHERE email = $1", (email,))
    if existing_user:
        logger.error("User already exists with email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    hashed_password = ph.hash(password)
    try :
        company = await execute_query(
            """
            INSERT INTO users (email, password_hash, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            (email, hashed_password, "", ""),
        )
        if not company:
            raise RuntimeError("Company insert did not return an id")

        await execute_query(
            """
            INSERT INTO users (company_id, name, email, password_hash)
            VALUES ($1, $2, $3, $4)
            """,
            (company[0]["id"], company_name, email, hashed_password),
        )

    except Exception as e:
        logger.error("Error occurred while registering user: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while registering user"
        )
    logger.info("User and workspace registered successfully: %s", email)

    # Generate token payload
    token = await create_jwt_token({"sub": email, "scopes": RECRUITER_SCOPES}, None)
    expires_in = int(os.getenv("JWT_EXPIRATION_MINUTES", 30)) * 60
    # Drop token directly into cookies so the user is logged in instantly
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,       
        expires=expires_in,
        max_age=expires_in,
        samesite="lax",       # Prevents CSRF vectors
        secure=False,         # Keep False for localhost, change to True for production
    )
    return {"message": "Registration and workspace provisioning successful", "token": token}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        samesite="lax",
        secure=False,
    )
    logger.info("User logged out successfully")
    return {"message": "Logout successful"}
