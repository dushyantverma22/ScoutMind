# app/api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import ScoutRequest, ScoutResponse, HealthResponse
from app.main import run_agent

import traceback
import os


# -------------------------------
# App Init
# -------------------------------
app = FastAPI(
    title="ScoutMind API",
    description="AI-Powered Talent Scouting & Engagement Agent",
    version="1.0.0"
)


# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# Serve Frontend Static Files
# -------------------------------
frontend_path = os.path.join(os.getcwd(), "frontend")

app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# -------------------------------
# Serve UI (index.html)
# -------------------------------
@app.get("/")
def serve_ui():
    return FileResponse(os.path.join(frontend_path, "index.html"))


# -------------------------------
# Health Check
# -------------------------------
@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "ok",
        "service": "scoutmind-api"
    }


# -------------------------------
# Main Endpoint
# -------------------------------
@app.post("/scout", response_model=ScoutResponse)
def scout_candidates(request: ScoutRequest):

    try:
        if not request.jd_text.strip():
            raise HTTPException(status_code=400, detail="JD text cannot be empty")

        result = run_agent(
            jd_text=request.jd_text,
            top_k=request.top_k
        )

        return {
            "session_id": result.get("session_id"),
            "node_status": result.get("node_status", {}),
            "jd_parsed": result.get("jd_parsed"),
            "final_output": result.get("final_output", []),
            "error": result.get("error"),
            "failed_node": result.get("failed_node")
        }

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Internal server error"
            }
        )


# -------------------------------
# Logs Endpoint
# -------------------------------
@app.get("/logs/{session_id}")
def get_logs(session_id: str):

    log_path = f"logs/{session_id}.log"

    if not os.path.exists(log_path):
        return {"logs": "No logs found"}

    with open(log_path, "r") as f:
        return {"session_id": session_id, "logs": f.read()}


# -------------------------------
# CSV Export Endpoint
# -------------------------------
@app.get("/export/{session_id}")
def export_csv(session_id: str):

    file_path = f"exports/{session_id}.csv"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=f"{session_id}.csv",
        media_type="text/csv"
    )