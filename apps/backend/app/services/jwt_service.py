from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from fastapi import HTTPException
import jwt
load_dotenv()

async def create_jwt_token(data : dict, expire_delta : timedelta) -> str:
    to_encode = data.copy()

    if expire_delta is None:
        expire_delta = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    expire = datetime.utcnow() + expire_delta

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

    return encoded_jwt

async def verify_jwt_token(token: str) -> bool:
    """A protected endpoint that validates the token signature and expiration."""
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        useremail: str = payload.get("sub")
        if useremail is None:
            raise HTTPException(status_code=401, detail="Invalid token claims")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
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