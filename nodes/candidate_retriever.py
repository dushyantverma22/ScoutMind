# nodes/candidate_retriever.py

import pandas as pd
import re
from typing import Dict, Any, List
from graph.state import AgentState
from utils.s3_utils import download_file


# -------------------------------
# Load Dataset (once)
# -------------------------------
def load_candidates():
    from utils.s3_utils import download_file

    download_file("data/candidates.csv", "temp/candidates.csv")

    df = pd.read_csv("temp/candidates.csv",  encoding="latin1")
   # df = pd.read_csv("data/candidates.csv", encoding="latin1")

    grouped = df.groupby("id").agg({
        "candidate_name": "first",
        "skill_name": lambda x: list(set([str(s).lower() for s in x.dropna()])),
        "certification_name": lambda x: list(set(x.dropna()))
    }).reset_index()

    candidates = []

    for _, row in grouped.iterrows():

        skills = [s.strip().lower() for s in row["skill_name"]]

        candidate = {
            "name": row["candidate_name"],
            "skills": skills,
            "experience": 2,  # you can randomize if needed
            "summary": f"Skilled in {', '.join(skills[:5])}",
            "current_role": "Data Professional"
        }

        candidates.append(candidate)

    return candidates


# -------------------------------
# Keyword Matching
# -------------------------------
def keyword_filter(candidates, required_skills, skill_map):

    shortlisted = []

    for c in candidates:

        text = " ".join(c["skills"]).lower()

        matched = []

        for skill in required_skills:
            synonyms = skill_map.get(skill.lower(), [skill.lower()])

            pattern = r"\b(" + "|".join(re.escape(s) for s in synonyms) + r")\b"

            if re.search(pattern, text):
                matched.append(skill)

        ratio = len(matched) / len(required_skills) if required_skills else 0

        if ratio >= 0.4:  # threshold
            shortlisted.append(c)

    return shortlisted


# -------------------------------
# Node
# -------------------------------
def candidate_retriever_node(state: AgentState) -> Dict[str, Any]:

    logger = state.get("logger")

    try:
        logger.info("Candidate Retriever started")

        jd = state["jd_parsed"]
        skill_map = state.get("skill_synonyms", {})

        required_skills = jd.get("required_skills", [])

        candidates = load_candidates()

        logger.info(f"Total candidates loaded: {len(candidates)}")

        filtered = keyword_filter(candidates, required_skills, skill_map)

        logger.info(f"Candidates after filter: {len(filtered)}")

        # Limit for performance
        filtered = filtered[:100]

        return {
            "candidates_raw": filtered,
            "node_status": {**(state.get("node_status") or {}), "candidate_retriever": "ok"}
        }

    except Exception as e:
        logger.error(f"Candidate Retriever failed: {str(e)}")

        return {
            "error": str(e),
            "failed_node": "candidate_retriever",
            "node_status": {**(state.get("node_status") or {}), "candidate_retriever": "failed"}
        }