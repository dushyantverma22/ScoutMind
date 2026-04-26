# graph/memory.py

from langgraph.checkpoint.memory import InMemorySaver


def get_memory():
    """
    Returns an in-memory checkpointer for LangGraph.
    This avoids local SQLite disk I/O issues during development runs.
    """

    return InMemorySaver()
