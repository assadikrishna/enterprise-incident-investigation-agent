
from collections.abc import Callable

from src.protocol import SYSTEM_PROMPT, parse_response
from src.graph.state import InvestigationState


GenerateFunction = Callable[[str], str]

MAX_FORMAT_RETRIES = 3


def make_reasoning_node(generate: GenerateFunction):
    """Create a reasoning node using the supplied LLM function."""

    def reasoning_node(
        state: InvestigationState,
    ) -> dict:
        """Generate and validate the next investigation action."""

        incident_request = state["incident_request"]
        trace = state["trace"]

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            "===== CURRENT USER REQUEST =====\n"
            f"{incident_request}\n"
            "===== END CURRENT USER REQUEST =====\n\n"
            "Use all concrete values in the current user request, "
            "including any incident ID. Do not ask for information "
            "already provided.\n\n"
        )

        correction = ""

        for attempt in range(1, MAX_FORMAT_RETRIES + 1):
            response = generate(
                prompt + trace + correction
            )

            try:
                thought, action = parse_response(response)

                return {
                    "thought": thought,
                    "action": action,
                    "status": "action_ready",
                }

            except ValueError as exc:
                if attempt == MAX_FORMAT_RETRIES:
                    raise RuntimeError(
                        "Model failed to produce a valid "
                        "Thought/Action response after "
                        f"{MAX_FORMAT_RETRIES} attempts."
                    ) from exc

                correction = (
                    "\n\nSYSTEM CORRECTION:\n"
                    "Your previous response violated the "
                    "required ReAct protocol.\n"
                    "Output exactly one Thought and one Action.\n"
                    "Do not generate an Observation.\n"
                    "Do not generate another Thought or Action.\n"
                    "Stop immediately after the Action.\n"
                )

        raise RuntimeError(
            "Reasoning node ended without a valid action."
        )

    return reasoning_node


def make_tool_node(execute):
    """Create a tool node using the supplied action executor."""

    def tool_node(
        state: InvestigationState,
    ) -> dict:
        """Execute one validated investigation action."""

        action = state["action"]

        # Preserve the original minimum-evidence guardrail.
        if action.lower().startswith("finish["):
            missing_evidence = []

            if not state["has_incident_details"]:
                missing_evidence.append("incident details")

            if not state["has_log_evidence"]:
                missing_evidence.append("direct log evidence")

            if missing_evidence:
                observation = (
                    "GUARDRAIL_BLOCKED: Cannot finish the "
                    "investigation yet. Missing required evidence: "
                    + ", ".join(missing_evidence)
                    + ". Continue investigating."
                )

                return {
                    "observation": observation,
                    "status": "observation_ready",
                }

        observation = execute(
            action,
            current_evidence=state["evidence_trace"],
        )

        if observation.startswith("FINISH:"):
            return {
                "observation": observation,
                "final_answer": observation.removeprefix(
                    "FINISH:"
                ).strip(),
                "status": "finished",
            }

        if observation.startswith("USER_INPUT_REQUIRED:"):
            return {
                "observation": observation,
                "status": "human_input_required",
            }

        return {
            "observation": observation,
            "status": "observation_ready",
        }

    return tool_node


def update_state_node(state: InvestigationState) -> dict:
    """Record the latest reasoning step and tool observation."""

    thought = state["thought"]
    action = state["action"]
    observation = state["observation"]

    step = state["step"] + 1

    new_trace = (
        state["trace"]
        + f"\nStep {step}\n"
        + f"Thought: {thought}\n"
        + f"Action: {action}\n"
        + f"Observation: {observation}\n"
    )

    new_evidence_trace = state["evidence_trace"]

    if not observation.startswith(
        (
            "GUARDRAIL_BLOCKED:",
            "ERROR:",
            "USER_INPUT_REQUIRED:",
        )
    ):
        new_evidence_trace += (
            f"\nAction: {action}\n"
            f"Observation: {observation}\n"
        )

    # Initialize both flags regardless of the observation result.
    has_incident_details = state.get(
        "has_incident_details", False
    )

    has_log_evidence = state.get(
        "has_log_evidence", False
    )

    valid_observation = (
        bool(observation.strip())
        and not observation.startswith(
            (
                "GUARDRAIL_BLOCKED:",
                "ERROR:",
                "USER_INPUT_REQUIRED:",
            )
        )
    )

    if valid_observation:
        if action.startswith("get_incident_details["):
            if "No incident found" not in observation:
                has_incident_details = True

        if action.startswith("search_logs["):
            if (
                not observation.startswith(
                    "No log search query was provided."
                )
                and not observation.startswith(
                    "No log entries matched"
                )
            ):
                has_log_evidence = True

    return {
        "trace": new_trace,
        "evidence_trace": new_evidence_trace,
        "step": step,
        "has_incident_details": has_incident_details,
        "has_log_evidence": has_log_evidence,
    }