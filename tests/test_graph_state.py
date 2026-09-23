from src.graph.nodes import update_state_node


def test_state_update_records_observation():

    state = {
        "thought": "I should retrieve incident details.",
        "action": "get_incident_details[INC-001]",
        "observation": "Service: payment-service",
        "trace": "",
        "evidence_trace": "",
        "step": 0,
    }

    result = update_state_node(state)

    assert result["step"] == 1

    assert "Step 1" in result["trace"]
    assert "get_incident_details[INC-001]" in result["trace"]
    assert "Service: payment-service" in result["trace"]

    assert "Service: payment-service" in result["evidence_trace"]

    print("PASS: State update recorded the tool observation.")


def test_state_update_excludes_guardrail_from_evidence():

    state = {
        "thought": "I have enough information.",
        "action": "finish[Investigation complete.]",
        "observation": (
            "GUARDRAIL_BLOCKED: Missing direct log evidence."
        ),
        "trace": "",
        "evidence_trace": "",
        "step": 1,
    }

    result = update_state_node(state)

    assert result["step"] == 2

    assert "GUARDRAIL_BLOCKED:" in result["trace"]

    assert "GUARDRAIL_BLOCKED:" not in result["evidence_trace"]

    print("PASS: Guardrail message excluded from evidence.")


def test_incident_details_set_evidence_flag():
    state = {
        "thought": "Retrieve the incident.",
        "action": "get_incident_details[INC-001]",
        "observation": "Service: payment-service",
        "trace": "",
        "evidence_trace": "",
        "step": 0,
        "has_incident_details": False,
        "has_log_evidence": False,
    }

    result = update_state_node(state)

    assert result["has_incident_details"] is True
    assert result["has_log_evidence"] is False

    print("PASS: Incident details flag updated.")


def test_log_search_sets_evidence_flag():
    state = {
        "thought": "Inspect the service logs.",
        "action": "search_logs[payment-service]",
        "observation": "Database connection pool exhausted.",
        "trace": "",
        "evidence_trace": "",
        "step": 1,
        "has_incident_details": True,
        "has_log_evidence": False,
    }

    result = update_state_node(state)

    assert result["has_incident_details"] is True
    assert result["has_log_evidence"] is True

    print("PASS: Log evidence flag updated.")

def test_missing_incident_does_not_set_evidence_flag():
    state = {
        "thought": "Retrieve incident details.",
        "action": "get_incident_details[INC-999]",
        "observation": "No incident found for INC-999.",
        "trace": "",
        "evidence_trace": "",
        "step": 0,
        "has_incident_details": False,
        "has_log_evidence": False,
    }

    result = update_state_node(state)

    assert result["has_incident_details"] is False
    assert result["has_log_evidence"] is False

    print("PASS: Missing incident does not count as evidence.")


def test_missing_logs_do_not_set_evidence_flag():
    state = {
        "thought": "Search the service logs.",
        "action": "search_logs[unknown-service]",
        "observation": "No log entries matched for unknown-service.",
        "trace": "",
        "evidence_trace": "",
        "step": 1,
        "has_incident_details": True,
        "has_log_evidence": False,
    }

    result = update_state_node(state)

    assert result["has_incident_details"] is True
    assert result["has_log_evidence"] is False

    print("PASS: Missing logs do not count as evidence.")

def test_empty_log_query_does_not_set_evidence_flag():
    state = {
        "thought": "Search the service logs.",
        "action": "search_logs[]",
        "observation": "No log search query was provided.",
        "trace": "",
        "evidence_trace": "",
        "step": 1,
        "has_incident_details": True,
        "has_log_evidence": False,
    }

    result = update_state_node(state)

    assert result["has_log_evidence"] is False

    print("PASS: Empty log query does not count as evidence.")