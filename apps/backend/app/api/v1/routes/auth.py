import os
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends, Form
from db.session import get_pg_connection
from services.pg_db_service import execute_query
from services.jwt_service import create_jwt_token, deactivate_jwt_token, verify_jwt_token
from argon2 import PasswordHasher
import logging
router = APIRouter()
logger = logging.getLogger(__name__)
ph = PasswordHasher()

@router.post("/login")
async def login(email: str = Form(...), password: str = Form(...), response: Response = None):
    pg_connection = get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database connection failed"
        )

    # 2. Extract values using standard fields: .username and .password
    # Since frontend appends email as "username", read form_data.username
    user = execute_query("SELECT * FROM users WHERE email = %s", (email,))
    if not user:
        logger.error("Invalid login credentials")
        return {"message": "Invalid email or password"}, status.HTTP_401_UNAUTHORIZED
    
    userpassword = user[0][2] 
    if not ph.verify(userpassword, password):
        logger.error("Invalid login credentials for email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    token = await create_jwt_token({"sub": email}, None)
    
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
    pg_connection = get_pg_connection()
    if pg_connection is None:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )

    # Check for existing user collision
    existing_user = execute_query("SELECT * FROM users WHERE email = %s", (email,))
    if existing_user:
        logger.error("User already exists with email: %s", email)
        return {"message": "User already exists with this email"}, status.HTTP_400_BAD_REQUEST
    
    hashed_password = ph.hash(password)
    execute_query(
        "INSERT INTO users (name, email, company_name, password) VALUES (%s, %s, %s, %s)", 
        (email, email, company_name, hashed_password)
    )
    logger.info("User and workspace registered successfully: %s", email)

    # Generate token payload
    token = await create_jwt_token({"sub": email}, None)
    expires_in = os.getenv("JWT_EXPIRATION_MINUTES", 30) * 60
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
async def logout(token: str):
    await deactivate_jwt_token(token)
    logger.info("User logged out successfully")
    return {"message": "Logout successful"}