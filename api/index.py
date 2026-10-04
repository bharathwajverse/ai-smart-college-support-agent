import os
import sys
from fastapi import Request

# Ensure the project root directory is on the Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.main import app


@app.middleware("http")
async def handle_vercel_routing(request: Request, call_next):
    """
    Normalizes paths for Vercel serverless functions.
    Extracts the matched subpath from the rewrite parameter and updates
    request.scope['path'] so that FastAPI routes match cleanly.
    """
    match = request.query_params.get("match")
    if match:
        clean = match.lstrip("/")
        if clean in ["docs", "openapi.json"]:
            request.scope["path"] = f"/{clean}"
        else:
            request.scope["path"] = f"/api/{clean}"
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
