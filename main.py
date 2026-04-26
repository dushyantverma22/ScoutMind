# app/main.py

# app/main.py

from dotenv import load_dotenv
load_dotenv()

import uuid
from datetime import datetime


from graph.graph_builder import build_graph
from utils.logger import get_logger


def run_agent(jd_text: str, top_k: int = 5):

    # -------------------------------
    # Session Setup
    # -------------------------------
    session_id = str(uuid.uuid4())

    logger = get_logger(session_id)

    logger.info("Starting new session")

    # -------------------------------
    # Initial State
    # -------------------------------
    state = {
        "session_id": session_id,
        "started_at": datetime.utcnow().isoformat(),
        "jd_raw": jd_text,
        "top_k": top_k,
        "logger": logger
    }

    # -------------------------------
    # Build Graph
    # -------------------------------
    graph = build_graph()

    # -------------------------------
    # Execute
    # -------------------------------
    result = graph.invoke(
        state,
        config={
            "configurable": {
                "thread_id": session_id
            }
        }
    )

    logger.info("Session completed")

    return result


# -------------------------------
# CLI TEST (for now)
# -------------------------------
if __name__ == "__main__":

    jd_text = """We are hiring a Data Scientist with experience in Python, ML, SQL, and LLMs."""

    result = run_agent(jd_text, top_k=5)

    print("\n===== FINAL OUTPUT =====\n")

    for c in result.get("final_output", []):
        print(f"⭐ {c['candidate_name']}")
        print(f"Match Score: {c['match_score']}")
        print(f"Interest Score: {c['interest_score']}")
        print(f"Final Score: {c['final_score']}")
        print(f"Status: {c['status']}")
        print(f"Insight: {c['explanation']}")
        print(f"Summary: {c['conversation_summary']}")
        print("=" * 60)