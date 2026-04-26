# nodes/scorer.py

from typing import Dict, Any
from graph.state import AgentState
from llm.scoring_chain import scoring_chain


def scoring_node(state: AgentState) -> Dict[str, Any]:

    logger = state.get("logger")

    try:
        logger.info("Scoring node started")

        jd = state["jd_parsed"]
        candidates = state.get("candidates_raw", [])

        if not candidates:
            logger.warning("No candidates to score")

            return {
                "scored_candidates": [],
                "node_status": {**(state.get("node_status") or {}), "scorer": "skipped"}
            }

        scored = []

        # Limit LLM calls
        candidates = candidates[:state.get("top_k", 5) * 3]

        for c in candidates:

            try:
                result = scoring_chain.invoke({
                    "jd": str(jd),
                    "candidate": str(c)
                })

                scored.append({
                    **c,
                    "match_score": result.match_score,
                    "matched_skills": result.matched_skills,
                    "missing_skills": result.missing_skills,
                    "match_explanation": result.explanation
                })

            except Exception as inner_e:
                logger.error(f"Candidate scoring failed: {str(inner_e)}")

        logger.info(f"Scoring completed: {len(scored)} candidates")

        # Sort by match score
        scored = sorted(scored, key=lambda x: x["match_score"], reverse=True)

        return {
            "scored_candidates": scored,
            "node_status": {**(state.get("node_status") or {}), "scorer": "ok"}
        }

    except Exception as e:
        logger.error(f"Scoring node failed: {str(e)}")

        return {
            "error": str(e),
            "failed_node": "scorer",
            "node_status": {**(state.get("node_status") or {}), "scorer": "failed"}
        }