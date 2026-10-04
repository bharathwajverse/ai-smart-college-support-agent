import os
import sys

# Ensure the project root directory is on the Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.main import app

@app.middleware("http")
async def ensure_api_prefix(request, call_next):
    """
    Ensures that requests forwarded by Vercel serverless function router
    correctly match FastAPI route definitions regardless of whether the /api
    prefix was preserved or stripped.
    """
    path = request.scope.get("path", "")
    if path and not path.startswith("/api") and not path.startswith("/docs") and not path.startswith("/openapi.json"):
        request.scope["path"] = "/api" + path
    return await call_next(request)


@app.get("/api")
def api_root():
    """Health and status endpoint for CampusResolve AI."""
    return {
        "status": "online",
        "service": "CampusResolve AI - Smart College Support & Grievance Agent",
        "version": "1.0.0",
        "endpoints": {
            "complaints": "/api/complaints",
            "chat": "/api/chat",
            "metrics": "/api/metrics",
            "fai_diagnostics": "/api/fai-diagnostics",
            "csp_dispatch": "/api/csp/dispatch",
            "planning_search": "/api/planning/compare-search",
            "inference": "/api/inference/backward-chain",
            "documentation": "/docs"
        }
    }
