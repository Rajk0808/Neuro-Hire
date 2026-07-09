from fastapi import Request, Response
from fastapi.responses import JSONResponse
from services.jwt_service import decode_jwt_token
from middleware import EXTEMPTED_ROUTES, SCOPE_REGISTRY
from starlette.middleware.base import BaseHTTPMiddleware
import re

def _required_scopes_for_path(path: str):
    if path in SCOPE_REGISTRY:
        return SCOPE_REGISTRY[path]

    for route_path, scopes in SCOPE_REGISTRY.items():
        pattern = "^" + re.sub(r"\{[^/]+\}", r"[^/]+", route_path) + "$"
        if re.match(pattern, path):
            return scopes

    return []

class Oauth2Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path.lstrip("/")

        if path in EXTEMPTED_ROUTES:
            return await call_next(request)
        
        required_scopes = _required_scopes_for_path(path)

        auth_header = request.headers.get("Authorization")
        token = request.cookies.get("access_token")
        if not token and auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        if not token:
            return JSONResponse(status_code=401, content={"detail": "Authentication token missing"})

        try:
            payload = decode_jwt_token(token)
            user_scopes = payload.get('scopes', [])
            
            for scope in required_scopes:
                if scope not in user_scopes:
                    return JSONResponse(status_code=403, content={"detail": f"Insufficient scope. Required: {', '.join(required_scopes)}"})
            response: Response = await call_next(request)
            return response
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        
