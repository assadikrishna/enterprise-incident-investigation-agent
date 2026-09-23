from src.graph.workflow import build_investigation_graph


def test_graph_requests_human_input():
    """Verify that the compiled graph runs and stops for human input."""

    calls = []

    def fake_generate(prompt: str) -> str:
        calls.append("reasoning")

        return (
            "Thought: I need clarification from the engineer.\n"
            "Action: ask_user[Please provide the incident ID.]"
        )

    def fake_execute(action: str, current_evidence="") -> str:
        calls.append("tool_execution")

        assert action == (
            "ask_user[Please provide the incident ID.]"
        )

        return (
            "USER_INPUT_REQUIRED: "
            "Please provide the incident ID."
        )

    graph = build_investigation_graph(
        fake_generate,
        fake_execute,
    )

    initial_state = {
        "incident_request": "Investigate an incident.",
        "trace": "",
        "evidence_trace": "",
        "thought": "",
        "action": "",
        "observation": "",
        "step": 0,
        "max_steps": 6,
        "has_incident_details": False,
        "has_log_evidence": False,
        "status": "",
        "final_answer": "",
    }

    result = graph.invoke(initial_state)

    assert result["status"] == "human_input_required"

    assert result["step"] == 1

    assert result["final_answer"] == ""

    assert (
        "USER_INPUT_REQUIRED:"
        in result["observation"]
    )

    assert "ask_user[" in result["trace"]

    assert calls == [
        "reasoning",
        "tool_execution",
    ]

    print(
        "PASS: LangGraph executed the investigation "
        "and stopped for human input."
    )

def test_graph_completes_three_step_investigation():
    """Verify a full investigation using deterministic fake tools."""

    actions = iter(
        [
            (
                "Thought: Retrieve incident details.\n"
                "Action: get_incident_details[INC-001]"
            ),
            (
                "Thought: Inspect the service logs.\n"
                "Action: search_logs[payment-service]"
            ),
            (
                "Thought: The evidence supports a conclusion.\n"
                "Action: finish[Likely database connection pool exhaustion.]"
            ),
        ]
    )

    executed_actions = []

    def fake_generate(prompt: str) -> str:
        return next(actions)

    def fake_execute(action: str, current_evidence="") -> str:
        executed_actions.append(action)

        if action == "get_incident_details[INC-001]":
            return (
                "Service: payment-service\n"
                "Summary: HTTP 503 errors after deployment."
            )

        if action == "search_logs[payment-service]":
            return "Database connection pool exhausted."

        if action.startswith("finish["):
            return (
                "FINISH: "
                "Likely database connection pool exhaustion."
            )

        return "ERROR: Unexpected action."

    graph = build_investigation_graph(
        fake_generate,
        fake_execute,
    )

    initial_state = {
        "incident_request": "Investigate incident INC-001",
        "trace": "",
        "evidence_trace": "",
        "thought": "",
        "action": "",
        "observation": "",
        "step": 0,
        "max_steps": 6,
        "has_incident_details": False,
        "has_log_evidence": False,
        "status": "",
        "final_answer": "",
    }

    result = graph.invoke(initial_state)

    assert result["status"] == "finished"
    assert result["step"] == 3

    assert result["has_incident_details"] is True
    assert result["has_log_evidence"] is True

    assert result["final_answer"] == (
        "Likely database connection pool exhaustion."
    )

    assert len(executed_actions) == 3

    assert "HTTP 503" in result["evidence_trace"]
    assert (
        "Database connection pool exhausted"
        in result["evidence_trace"]
    )

    print(
        "PASS: LangGraph completed a three-step investigation."
    )

def test_graph_escalates_at_max_steps():
    """Verify that the graph stops when the step limit is reached."""

    calls = []

    def fake_generate(prompt: str) -> str:
        calls.append("reasoning")

        return (
            "Thought: I need more incident information.\n"
            "Action: get_incident_details[INC-999]"
        )

    def fake_execute(action: str, current_evidence="") -> str:
        calls.append("tool_execution")

        return "No incident found for INC-999."

    graph = build_investigation_graph(
        fake_generate,
        fake_execute,
    )

    initial_state = {
        "incident_request": "Investigate incident INC-999",
        "trace": "",
        "evidence_trace": "",
        "thought": "",
        "action": "",
        "observation": "",
        "step": 0,
        "max_steps": 2,
        "has_incident_details": False,
        "has_log_evidence": False,
        "status": "",
        "final_answer": "",
    }

    result = graph.invoke(initial_state)

    assert result["status"] == "human_input_required"

    assert result["step"] == 2

    assert result["final_answer"].startswith(
        "USER_INPUT_REQUIRED:"
    )

    assert "maximum of 2 steps" in result["final_answer"]

    assert result["has_incident_details"] is False

    assert calls == [
        "reasoning",
        "tool_execution",
        "reasoning",
        "tool_execution",
    ]

    print(
        "PASS: LangGraph stopped after two steps "
        "and requested human input."
    )