# graph/graph_builder.py

from langgraph.graph import StateGraph

from graph.state import AgentState

# Import nodes
from nodes.jd_parser import jd_parser_node
from nodes.skill_expander import skill_expander_node
from nodes.candidate_retriever import candidate_retriever_node
from nodes.scorer import scoring_node
from nodes.outreach_agent import outreach_node
from nodes.reranker import reranker_node


# -------------------------------
# Conditional Router
# -------------------------------
def route_after_scoring(state: AgentState) -> str:

    logger = state.get("logger")

    candidates = state.get("scored_candidates")

    if not candidates:
        logger.info("No candidates found → skipping outreach")
        return "skip_outreach"

    logger.info(f"{len(candidates)} candidates found → running outreach")

    return "do_outreach"


def build_graph():

    graph = StateGraph(AgentState)

    # -------------------------------
    # Nodes
    # -------------------------------
    graph.add_node("jd_parser", jd_parser_node)
    graph.add_node("skill_expander", skill_expander_node)
    graph.add_node("candidate_retriever", candidate_retriever_node)
    graph.add_node("scorer", scoring_node)
    graph.add_node("outreach", outreach_node)
    graph.add_node("reranker", reranker_node)

    # -------------------------------
    # Flow
    # -------------------------------
    graph.set_entry_point("jd_parser")

    graph.add_edge("jd_parser", "skill_expander")
    graph.add_edge("skill_expander", "candidate_retriever")
    graph.add_edge("candidate_retriever", "scorer")

    # 🔥 CONDITIONAL EDGE HERE
    graph.add_conditional_edges(
        "scorer",
        route_after_scoring,
        {
            "do_outreach": "outreach",
            "skip_outreach": "reranker"
        }
    )

    # Continue flow
    graph.add_edge("outreach", "reranker")

    graph.set_finish_point("reranker")

    return graph.compile(checkpointer=False)
