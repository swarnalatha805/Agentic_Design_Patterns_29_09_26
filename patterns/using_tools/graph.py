from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import fallback_agent, math_agent, reasoning_agent


def route_question(state: AgentState) -> str:
    if state["intent"] == "math":
        return "math_agent"
    return "fallback_agent"

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("reasoning_agent", reasoning_agent)
    graph.add_node("math_agent", math_agent)
    graph.add_node("fallback_agent", fallback_agent)

    graph.set_entry_point("reasoning_agent")
    graph.add_conditional_edges(
        "reasoning_agent",
        route_question,
        {
            "math_agent": "math_agent",
            "fallback_agent": "fallback_agent",
        },
    )
    graph.add_edge("math_agent", END)
    graph.add_edge("fallback_agent", END)

    return graph.compile()
