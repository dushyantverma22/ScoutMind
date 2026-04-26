# nodes/skill_expander.py

from typing import Dict, Any
from graph.state import AgentState
from llm.skill_expander_chain import skill_chain


def build_default_skill_map(skills):
    return {skill.lower(): [skill.lower()] for skill in skills}


def skill_expander_node(state: AgentState) -> Dict[str, Any]:

    logger = state.get("logger")

    try:
        logger.info("Skill Expander started")

        jd = state["jd_parsed"]

        skills = jd.get("required_skills", [])
        role = jd.get("role", "")

        if not skills:
            logger.warning("No skills found in JD")

            return {
                "skill_synonyms": {},
                "node_status": {**(state.get("node_status") or {}), "skill_expander": "skipped"}
            }

        try:
            result = skill_chain.invoke({
                "role": role,
                "skills": skills
            })

            skill_map = result.skills or build_default_skill_map(skills)

        except Exception as inner_e:
            logger.warning(f"Skill expansion LLM failed; using default skill map: {str(inner_e)}")
            skill_map = build_default_skill_map(skills)

        logger.info(f"Skill expansion completed for {len(skill_map)} skills")

        return {
            "skill_synonyms": skill_map,
            "node_status": {**(state.get("node_status") or {}), "skill_expander": "ok"}
        }

    except Exception as e:
        logger.error(f"Skill Expander failed: {str(e)}")

        return {
            "error": str(e),
            "failed_node": "skill_expander",
            "node_status": {**(state.get("node_status") or {}), "skill_expander": "failed"}
        }
