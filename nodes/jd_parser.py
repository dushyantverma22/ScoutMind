# nodes/jd_parser.py

from typing import Dict, Any
from graph.state import AgentState


from llm.jd_parser_chain import jd_chain


def jd_parser_node(state: AgentState) -> Dict[str, Any]:

    logger = state.get("logger")

    try:
        logger.info("JD Parser started")

        jd_raw = state["jd_raw"]

        # LLM call
        jd_parsed = jd_chain.invoke({"jd": jd_raw})

        logger.info("JD Parser completed successfully")

        return {
            "jd_parsed": jd_parsed.model_dump(),
            "node_status": {**(state.get("node_status") or {}), "jd_parser": "ok"}
        }

    except Exception as e:
        logger.error(f"JD Parser failed: {str(e)}")

        return {
            "error": str(e),
            "failed_node": "jd_parser",
            "node_status": {**(state.get("node_status") or {}), "jd_parser": "failed"}
        }