# app/main.py

from dotenv import load_dotenv
load_dotenv()

from utils.s3_utils import upload_file
import uuid
from datetime import datetime

from graph.graph_builder import build_graph
from utils.logger import get_logger


# -------------------------------
# Save CSV + Upload to S3
# -------------------------------
def save_csv(session_id, final_output):

    import csv
    import os

    os.makedirs("exports", exist_ok=True)

    file_path = f"exports/{session_id}.csv"

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "candidate_name",
            "match_score",
            "interest_score",
            "final_score",
            "status",
            "explanation",
            "conversation_summary"
        ])

        for c in final_output:
            writer.writerow([
                c.get("candidate_name"),
                c.get("match_score"),
                c.get("interest_score"),
                c.get("final_score"),
                c.get("status"),
                c.get("explanation"),
                c.get("conversation_summary")
            ])

    # ✅ Upload CSV to S3
    try:
        upload_file(file_path, f"exports/{session_id}.csv")
    except Exception as e:
        print(f"CSV upload failed: {e}")


# -------------------------------
# Run Agent
# -------------------------------
def run_agent(jd_text: str, top_k: int = 5):

    session_id = str(uuid.uuid4())

    logger = get_logger(session_id)
    logger.info("Starting new session")

    state = {
        "session_id": session_id,
        "started_at": datetime.utcnow().isoformat(),
        "jd_raw": jd_text,
        "top_k": top_k,
        "logger": logger
    }

    graph = build_graph()

    result = graph.invoke(
        state,
        config={
            "configurable": {
                "thread_id": session_id
            }
        }
    )

    # ✅ Save CSV (this also uploads to S3)
    save_csv(session_id, result.get("final_output", []))

    logger.info("Session completed")

    # ✅ Upload logs to S3
    try:
        upload_file(f"logs/{session_id}.log", f"logs/{session_id}.log")
    except Exception as e:
        logger.error(f"Log upload failed: {e}")

    return result


# -------------------------------
# CLI TEST
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