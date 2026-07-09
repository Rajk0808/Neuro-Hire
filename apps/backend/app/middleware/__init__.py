EXTEMPTED_ROUTES = {
    "",
    "docs",
    "openapi.json",
    "v1/docs",
    "v1/openapi.json",
    "v1/login",
    "v1/register",
}

SCOPE_REGISTRY = {
    'v1/logout': ['user:read'],
    'v1/candidates': ['candidate:read'],
    'v1/create-candidate': ['candidate:write'],
    'v1/candidates/{candidate_id}': ['candidate:read', 'candidate:write', 'candidate:delete'],
    'v1/dashboard/open-roles': ['analytics:read'],  
    'v1/dashboard/candidates-count-current-week': ['analytics:read'],
    'v1/dashboard/average-time-to-hire': ['analytics:read'],
    'v1/dashboard/average-dei-score': ['analytics:read'],
    'v1/dashboard/recent-jobs': ['analytics:read'],
    'v1/dashboard/recent-recruiter-activities': ['analytics:read'],
    'v1/jobs': ['job:read'],
    'v1/create-job': ['job:write'],
    'v1/jobs/dei-score': ['job:read'],
    'v1/jobs/status/{session_id}': ['job:read'],
    'v1/jobs/review': ['job:write']
}

ALLOWED_SCOPES = {
    'user:read' : 'read-only access to user data',
    'user:write' : 'read and write access to user data',
    'admin:read' : 'read-only access to admin data',
    'admin:write' : 'read and write access to admin data',
    'job:read' : 'read-only access to job data',
    'job:write' : 'read and write access to job data',
    'candidate:read' : 'read-only access to candidate data',
    'candidate:write' : 'read and write access to candidate data',
    'interview:read' : 'read-only access to interview data',
    'interview:write' : 'read and write access to interview data',
    'analytics:read' : 'read-only access to analytics data'
}

from middleware.auth import Oauth2Middleware
from middleware.cors import CORSMiddleware

__all__ = ["Oauth2Middleware", "CORSMiddleware"]
