from collections.abc import Mapping

from langgraph.graph import END, START, StateGraph

from app.agents.planner_agent import PlannerAgent, planner_agent
from app.agents.response_generator import ResponseGenerator, response_generator
from app.graph.nodes import DEFAULT_TOOL_REGISTRY, ToolExecutor, create_planner_node, create_response_node, create_tool_node
from app.graph.state import RetailState


def create_graph(
    planner: PlannerAgent | None = None,
    tool_registry: Mapping[str, ToolExecutor] | None = None,
    responder: ResponseGenerator | None = None,
):
    """Build the fixed, auditable planner -> one tool -> responder workflow."""
    builder = StateGraph(RetailState)
    builder.add_node("planner", create_planner_node(planner or planner_agent))
    builder.add_node("tool", create_tool_node(tool_registry or DEFAULT_TOOL_REGISTRY))
    builder.add_node("response", create_response_node(responder or response_generator))
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "tool")
    builder.add_edge("tool", "response")
    builder.add_edge("response", END)
    return builder.compile()


graph = create_graph()
