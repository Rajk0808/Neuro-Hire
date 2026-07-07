from fastapi import Request, Response
from fastapi.responses import JSONResponse
from services.jwt_service import verify_jwt_token
from middleware import EXTEMPTED_ROUTES, SCOPE_REGISTRY
from starlette.middleware.base import BaseHTTPMiddleware

class Oauth2Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path.lstrip("/")

        if path in EXTEMPTED_ROUTES:
            return await call_next(request)
        
        required_scopes = SCOPE_REGISTRY.get(path, [])

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})
        
        token = auth_header.split(" ")[1]
        try:
            payload = verify_jwt_token(token)
            useremail = payload.get('useremail')
            user_scopes = payload.get('scopes', '')
            
            for scope in required_scopes:
                if scope not in user_scopes:
                    return JSONResponse(status_code=403, content={"detail": f"Insufficient scope. Required: {', '.join(required_scopes)}"})
            response: Response = await call_next(request)
            return response
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        