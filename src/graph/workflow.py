from langgraph.graph import StateGraph, START, END

from src.graph.state import InvestigationState
from src.graph.nodes import (
    make_reasoning_node,
    make_tool_node,
    update_state_node,
)


def route_after_update(state: InvestigationState) -> str:
    """Decide whether to continue or end the investigation."""

    if state["status"] in (
        "finished",
        "human_input_required",
    ):
        return "end"

    if state["step"] >= state["max_steps"]:
        return "max_steps"

    return "continue"


def max_steps_node(state: InvestigationState) -> dict:
    """Request human input when the step limit is reached."""

    message = (
        "USER_INPUT_REQUIRED: Investigation reached "
        f"the maximum of {state['max_steps']} steps "
        "without enough evidence to finish."
    )

    return {
        "status": "human_input_required",
        "final_answer": message,
    }


def build_investigation_graph(generate, execute):
    """Build a LangGraph investigation workflow."""

    builder = StateGraph(InvestigationState)

    builder.add_node(
        "reasoning",
        make_reasoning_node(generate),
    )

    builder.add_node(
        "tool_execution",
        make_tool_node(execute),
    )

    builder.add_node(
        "update_state",
        update_state_node,
    )

    builder.add_node(
        "max_steps",
        max_steps_node,
    )

    builder.add_edge(START, "reasoning")

    builder.add_edge(
        "reasoning",
        "tool_execution",
    )

    builder.add_edge(
        "tool_execution",
        "update_state",
    )

    builder.add_conditional_edges(
        "update_state",
        route_after_update,
        {
            "continue": "reasoning",
            "max_steps": "max_steps",
            "end": END,
        },
    )

    builder.add_edge("max_steps", END)

    return builder.compile()