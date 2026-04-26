from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScoutRequest(BaseModel):
    jd_text: str = Field(..., min_length=10, description="Raw job description text")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of candidates to return")


class CandidateResult(BaseModel):
    candidate_name: str
    match_score: int
    interest_score: int
    final_score: float
    status: str
    explanation: str
    conversation_summary: str


class ScoutResponse(BaseModel):
    session_id: str
    node_status: Dict[str, str] = Field(default_factory=dict)
    jd_parsed: Optional[Dict[str, Any]] = None
    final_output: List[CandidateResult] = Field(default_factory=list)
    error: Optional[str] = None
    failed_node: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
