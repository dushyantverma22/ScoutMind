# nodes/reranker.py

from typing import Dict, Any
from graph.state import AgentState
from llm.summary_chain import summary_chain


def assign_status(score: float) -> str:
    if score >= 85:
        return "High Priority"
    elif score >= 65:
        return "Consider"
    else:
        return "Low Priority"


def build_insight(c):

    matched = ", ".join(c.get("matched_skills", []))
    missing = c.get("missing_skills", [])

    if not missing:
        return f"Strong skill match ({matched}) with high interest."
    else:
        return f"Good match on {matched}, but missing {', '.join(missing)}. Candidate is still interested."


def reranker_node(state: AgentState) -> Dict[str, Any]:

    logger = state.get("logger")

    try:
        logger.info("Reranker started")

        candidates = state.get("scored_candidates", [])

        if not candidates:
            logger.warning("No candidates to rank")

            return {
                "final_output": [],
                "node_status": {**(state.get("node_status") or {}), "reranker": "skipped"}
            }

        final_output = []

        for c in candidates:

            match_score = c.get("match_score", 0)
            interest_score = c.get("interest_score", 0)

            final_score = round(0.6 * match_score + 0.4 * interest_score, 2)

            # -------------------------------
            # Conversation Summary
            # -------------------------------
            conversation = c.get("conversation_log", [])

            if len(conversation) > 1:
                try:
                    summary_obj = summary_chain.invoke({
                        "conversation": str(conversation)
                    })
                    summary = summary_obj.summary
                except:
                    summary = "Summary unavailable"
            else:
                summary = "No response from candidate"

            # -------------------------------
            # Build Output
            # -------------------------------
            final_output.append({
                "candidate_name": c.get("name"),
                "match_score": match_score,
                "interest_score": interest_score,
                "final_score": final_score,
                "status": assign_status(final_score),
                "explanation": build_insight(c),
                "conversation_summary": summary
            })

        # Sort
        final_output = sorted(final_output, key=lambda x: x["final_score"], reverse=True)

        logger.info("Reranker completed")

        return {
            "final_output": final_output,
            "node_status": {**(state.get("node_status") or {}), "reranker": "ok"}
        }

    except Exception as e:
        logger.error(f"Reranker failed: {str(e)}")

        return {
            "error": str(e),
            "failed_node": "reranker",
            "node_status": {**(state.get("node_status") or {}), "reranker": "failed"}
        }