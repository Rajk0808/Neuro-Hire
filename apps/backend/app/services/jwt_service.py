from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from fastapi import HTTPException, Request, status, Response
import jwt
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def _jwt_settings():
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM", "HS256")
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is required")
    return secret_key, algorithm

async def create_jwt_token(data : dict, expire_delta : timedelta) -> str:
    to_encode = data.copy()

    if expire_delta is None:
        expire_delta = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    expire = datetime.utcnow() + expire_delta

    to_encode.update({"exp": expire})

    secret_key, algorithm = _jwt_settings()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt

def decode_jwt_token(token: str) -> dict:
    secret_key, algorithm = _jwt_settings()
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    if payload.get("sub") is None:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    return payload

async def verify_jwt_token(request : Request, response : Response) -> bool:
    """A protected endpoint that validates the token signature and expiration."""
    try:
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
        if not token:
            logger.warning("Authentication failed: Cookie missing.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token missing"
            )
        payload = decode_jwt_token(token)
        useremail: str = payload.get("sub")
    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: Token has expired.")
        raise HTTPException(status_code=401, detail="Authentication token expired")
    except jwt.InvalidTokenError:
        logger.warning("Authentication failed: Invalid token.")
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"useremail": useremail, "status": "Successfully authenticated!"}

async def deactivate_jwt_token(token: str) -> dict:
    """Decode the JWT token and return the payload."""
    try:
        timedelta = timedelta(minutes=int(0))
        token.update({"exp": timedelta})
        return token
    except jwt.InvalidTokenError:
        return {"message": "Invalid token"}
