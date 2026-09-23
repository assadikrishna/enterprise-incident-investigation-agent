
from src.graph.nodes import make_tool_node


def test_tool_node_executes_action():

    calls = []

    def fake_execute(action, current_evidence=""):
        calls.append((action, current_evidence))

        return (
            "service: payment-service\n"
            "severity: high\n"
            "summary: HTTP 503 errors"
        )

    tool_node = make_tool_node(fake_execute)

    state = {
        "action": "get_incident_details[INC-001]",
        "evidence_trace": "Current user request: Investigate INC-001",
        "has_incident_details": False,
        "has_log_evidence": False,
    }

    result = tool_node(state)

    assert result["status"] == "observation_ready"

    assert "payment-service" in result["observation"]

    assert calls == [
        (
            "get_incident_details[INC-001]",
            "Current user request: Investigate INC-001",
        )
    ]

    print("PASS: Tool node executed the selected action.")



def test_finish_blocked_without_required_evidence():
    """The agent must not finish without required evidence."""

    calls = []

    def fake_execute(action, current_evidence=""):
        calls.append(action)
        return "FINISH: Investigation complete."

    tool_node = make_tool_node(fake_execute)

    state = {
        "action": "finish[The deployment caused the incident.]",
        "evidence_trace": "Current user request: Investigate INC-001",
        "has_incident_details": False,
        "has_log_evidence": False,
    }

    result = tool_node(state)

    assert result["status"] == "observation_ready"

    assert result["observation"].startswith(
        "GUARDRAIL_BLOCKED:"
    )

    assert "incident details" in result["observation"]
    assert "direct log evidence" in result["observation"]

    # The finish action must never reach the executor.
    assert calls == []

    print(
        "PASS: Finish blocked when required evidence is missing."
    )

def test_finish_allowed_with_required_evidence():
    """Allow completion when incident and log evidence exist."""

    calls = []

    def fake_execute(action, current_evidence=""):
        calls.append((action, current_evidence))
        return "FINISH: Likely database connection pool exhaustion."

    tool_node = make_tool_node(fake_execute)

    state = {
        "action": "finish[Likely database connection pool exhaustion.]",
        "evidence_trace": (
            "Incident details: HTTP 503 after deployment.\n"
            "Logs: Database connection pool exhausted."
        ),
        "has_incident_details": True,
        "has_log_evidence": True,
    }

    result = tool_node(state)

    assert result["status"] == "finished"

    assert result["final_answer"] == (
        "Likely database connection pool exhaustion."
    )

    assert len(calls) == 1

    print(
        "PASS: Finish allowed when required evidence is present."
    )