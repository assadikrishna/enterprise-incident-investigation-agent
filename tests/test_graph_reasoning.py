from src.graph.nodes import make_reasoning_node
import pytest


def fake_generate(prompt: str) -> str:
    """Return a predictable response without calling an LLM."""

    assert "Investigate incident INC-001" in prompt

    return (
        "Thought: I should retrieve the incident details first.\n"
        "Action: get_incident_details[INC-001]"
    )


def test_reasoning_node():
    reasoning_node = make_reasoning_node(fake_generate)

    state = {
        "incident_request": "Investigate incident INC-001",
        "trace": "",
    }

    result = reasoning_node(state)

    assert result["action"] == "get_incident_details[INC-001]"
    assert result["status"] == "action_ready"
    assert result["thought"]

    print("PASS: Reasoning node selected the correct action.")


def test_rejects_fabricated_observation():
    """Reject model-generated observations and retry safely."""

    calls = []

    def fake_generate_with_fabrication(prompt: str) -> str:
        calls.append(prompt)

        return (
            "Thought: I should retrieve the incident details.\n"
            "Action: get_incident_details[INC-001]\n"
            "Observation: The database is unavailable."
        )

    reasoning_node = make_reasoning_node(
        fake_generate_with_fabrication
    )

    state = {
        "incident_request": "Investigate incident INC-001",
        "trace": "",
    }

    with pytest.raises(
        RuntimeError,
        match="Model failed to produce a valid",
    ):
        reasoning_node(state)

    assert len(calls) == 3

    print(
        "PASS: Fabricated observation rejected after "
        "three invalid responses."
    )


if __name__ == "__main__":
    test_reasoning_node()