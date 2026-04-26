"""
AgentState — the single object that flows through every LangGraph node.
All fields are Optional so nodes can be added/skipped without breaking the graph.
"""

from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime


class CandidateRecord(TypedDict):
    name: str
    skills: List[str]
    experience: int
    summary: str
    current_role: str


class ScoredCandidate(TypedDict):
    name: str
    skills: List[str]
    experience: int
    summary: str
    current_role: str
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    match_explanation: str
    interest_score: int
    interest_explanation: str
    conversation_log: List[Dict[str, str]]
    response_status: str          # "Responded" | "No Response" | "Not Contacted"
    final_score: float


class FinalOutput(TypedDict):
    candidate_name: str
    match_score: int
    interest_score: int
    final_score: float
    status: str                   # "High Priority" | "Consider" | "Low Priority"
    explanation: str
    conversation_summary: str


class AgentState(TypedDict):
    # ── Session metadata ──────────────────────────────────────────────────────
    session_id: str
    started_at: str
    completed_at: Optional[str]

    # ── Inputs ────────────────────────────────────────────────────────────────
    jd_raw: str
    top_k: int

    # ── Core System ───────────────────────────────────────────────────────────
    logger: Any

    # ── Node 1 output ─────────────────────────────────────────────────────────
    jd_parsed: Optional[Dict[str, Any]]
    skill_synonyms: Optional[Dict[str, List[str]]]

    # ── Node 2 output ─────────────────────────────────────────────────────────
    candidates_raw: Optional[List[CandidateRecord]]

    # ── Node 3 output ─────────────────────────────────────────────────────────
    scored_candidates: Optional[List[ScoredCandidate]]

    # ── Node 5 output ─────────────────────────────────────────────────────────
    final_output: Optional[List[FinalOutput]]

    # ── Error tracking ────────────────────────────────────────────────────────
    error: Optional[str]
    failed_node: Optional[str]
    node_status: Optional[Dict[str, str]]