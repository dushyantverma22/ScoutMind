# nodes/outreach_agent.py

import json
import random
from typing import Dict, Any
from graph.state import AgentState
from llm.outreach_chain import reply_chain, score_chain


def outreach_node(state: AgentState) -> Dict[str, Any]:

    logger = state.get("logger")

    try:
        logger.info("Outreach node started")

        jd = state["jd_parsed"]
        candidates = state.get("scored_candidates", [])

        if not candidates:
            logger.warning("No candidates for outreach")

            return {
                "scored_candidates": [],
                "node_status": {**(state.get("node_status") or {}), "outreach": "skipped"}
            }

        updated = []

        for c in candidates:

            # Skip low match
            if c["match_score"] < 40:
                c["interest_score"] = 0
                c["interest_explanation"] = "Low match score"
                c["conversation_log"] = []
                c["response_status"] = "Not Contacted"
                updated.append(c)
                continue

            # Simulate no response
            if random.random() < 0.2:
                c["interest_score"] = 0
                c["interest_explanation"] = "No response"
                c["conversation_log"] = [
                    {"role": "agent", "content": "Initial outreach sent"}
                ]
                c["response_status"] = "No Response"
                updated.append(c)
                continue

            try:
                # -------------------------------
                # Message
                # -------------------------------
                message = f"""
Hi {c['name']},

We have a {jd.get('seniority', 'mid-level')} {jd.get('role')} role.

Your experience in {', '.join(c['skills'][:2])} looks like a strong fit.

Interested?
"""

                # -------------------------------
                # Reply
                # -------------------------------
                reply_obj = reply_chain.invoke({
                    "candidate": json.dumps(c),
                    "message": message
                })

                reply = reply_obj.reply

                conversation = [
                    {"role": "agent", "content": message},
                    {"role": "candidate", "content": reply}
                ]

                # -------------------------------
                # Score
                # -------------------------------
                score_obj = score_chain.invoke({
                    "conversation": json.dumps(conversation)
                })

                c["interest_score"] = score_obj.interest_score
                c["interest_explanation"] = score_obj.explanation
                c["conversation_log"] = conversation
                c["response_status"] = "Responded"

            except Exception as inner_e:
                logger.error(f"Outreach failed for candidate: {str(inner_e)}")

                c["interest_score"] = 0
                c["interest_explanation"] = "Error during outreach"
                c["response_status"] = "Failed"

            updated.append(c)

        logger.info("Outreach completed")

        return {
            "scored_candidates": updated,
            "node_status": {**(state.get("node_status") or {}), "outreach": "ok"}
        }

    except Exception as e:
        logger.error(f"Outreach node failed: {str(e)}")

        return {
            "error": str(e),
            "failed_node": "outreach",
            "node_status": {**(state.get("node_status") or {}), "outreach": "failed"}
        }