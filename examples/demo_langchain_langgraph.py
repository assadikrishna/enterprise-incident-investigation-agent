from src.agent import execute_action
from src.graph.workflow import build_investigation_graph
from src.langchain_llm import generate_with_langchain


def main() -> None:
    incident_request = "Investigate incident INC-001."

    graph = build_investigation_graph(
        generate=generate_with_langchain,
        execute=execute_action,
    )

    initial_state = {
        "incident_request": incident_request,
        "trace": "",
        "evidence_trace": (
            f"Current user request:\n{incident_request}\n\n"
        ),
        "thought": "",
        "action": "",
        "observation": "",
        "step": 0,
        "max_steps": 6,
        "has_incident_details": False,
        "has_log_evidence": False,
        "status": "started",
        "final_answer": "",
    }

    print("Starting LangGraph investigation...")
    print(f"Request: {incident_request}")

    result = graph.invoke(initial_state)

    print("\n===== INVESTIGATION TRACE =====")
    print(result["trace"])

    print("\n===== FINAL STATUS =====")
    print(result["status"])

    print("\n===== FINAL ANSWER =====")
    print(result["final_answer"] or "No final answer generated.")


if __name__ == "__main__":
    main()