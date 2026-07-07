from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from fastapi import HTTPException, Request, status, Response
import jwt
import logging

load_dotenv()
logger = logging.getLogger(__name__)

async def create_jwt_token(data : dict, expire_delta : timedelta) -> str:
    to_encode = data.copy()

    if expire_delta is None:
        expire_delta = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    expire = datetime.utcnow() + expire_delta

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

    return encoded_jwt

async def verify_jwt_token(request : Request, response : Response) -> bool:
    """A protected endpoint that validates the token signature and expiration."""
    try:
        token = request.cookies.get("access_token")
        if not token:
            logger.warning("Authentication failed: Cookie missing.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token missing"
            )
    
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        useremail: str = payload.get("sub")
        if useremail is None:
            logger.warning("Authentication failed: Invalid token claims.")
            raise HTTPException(status_code=401, detail="Invalid token claims")
    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: Token has expired.")
        token = create_jwt_token({"sub": useremail, "scopes": payload.get("scopes")}, timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))))
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=1800,
            expires=1800,
            samesite="lax",
            secure=False,
        )
        return 
    except jwt.InvalidTokenError:
        logger.warning("Authentication failed: Invalid token.")
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError as e:
        logger.error(f"JWT Verification failed: {str(e)}")
        token = create_jwt_token({"sub": useremail}, timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))))
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=1800,
            expires=1800,
            samesite="lax",
            secure=False,
        )
    return {"useremail": useremail, "status": "Successfully authenticated!"}

async def deactivate_jwt_token(token: str) -> dict:
    """Decode the JWT token and return the payload."""
    try:
        timedelta = timedelta(minutes=int(0))
        token.update({"exp": timedelta})
        return token
    except jwt.InvalidTokenError:
        return {"message": "Invalid token"}