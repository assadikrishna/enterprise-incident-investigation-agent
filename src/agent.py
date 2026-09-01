from __future__ import annotations

import re
from collections.abc import Callable

from .tools import get_incident_details, get_runbook, search_logs, search_knowledge


GenerateFunction = Callable[[str], str]


SYSTEM_PROMPT = """
You are the Enterprise Incident Investigation Agent.

Your goal is to assist an engineer in investigating an incident.
Use a structured Reason-Act-Observe loop.

At each step:
1. Think step by step about the evidence currently available.
2. Select exactly one action.
3. Wait for the observation before deciding what to do next.
4. Do not invent tool results.
5. Do not make production changes.
6. Use finish[...] only when you have enough evidence to provide:
   - a concise incident summary,
   - the most likely cause or hypotheses,
   - supporting evidence,
   - recommended next investigation steps,
   - any remaining uncertainty.

Available actions:
- get_incident_details[<incident_id>]
- search_logs[<query>]
- get_runbook[<service>]
- search_knowledge[<query>]
- ask_user[<question>]
- finish[<answer>]


Important:
- Replace every value enclosed in < > with an actual value from the
user request or previous observations.
- Do not output placeholders literally.
- Never use literal placeholder words such as incident_id, query, service, question, or answer.
- Select exactly one action.
- Always inspect the CURRENT USER REQUEST before selecting an action.
- If the current request contains an incident ID, use that exact ID.
- Do not ask the user for information that is already present in the request
  or previous observations.
- Do not generate an Observation. Observations are produced only by application tools.
- Output only one Thought and one Action per response.
- Do not output any text after the Action.

Illustrative example only:

Example request:
Investigate incident INC-005.

Example response:
Thought: I should retrieve the incident details first.
Action: get_incident_details[INC-005]

The example is only a format demonstration. Always act on the CURRENT USER REQUEST.


Required response format:
Thought: <brief reasoning about the next investigation step>
Action: <one available action>

- Clearly separate observed evidence from inferred hypotheses.
- Do not state that a deployment caused the incident unless the evidence proves causation.
- Use phrases such as "may be related," "likely contributing factor," or
  "requires further verification" when evidence is incomplete.
- Production changes such as rollback, restart, scaling, or configuration
  changes require human review and approval.
- Do not imply that a check was performed unless a tool observation confirms it.
- When recommending checks that require unavailable tools or data, label them as suggested human investigation steps.
""".strip()


def execute_action(action: str, current_evidence: str = "") -> str:
    """Parse and execute one agent action."""
    action = action.strip()

    match = re.fullmatch(
        r"get_incident_details\[(.+)]", action, flags=re.IGNORECASE
    )
    if match:
        return get_incident_details(match.group(1).strip())

    match = re.fullmatch(r"search_logs\[(.+)]", action, flags=re.IGNORECASE)
    if match:
        return search_logs(match.group(1).strip())

    match = re.fullmatch(r"get_runbook\[(.+)]", action, flags=re.IGNORECASE)
    if match:
        return get_runbook(match.group(1).strip())

    match = re.fullmatch(r"search_knowledge\[(.+)]", action, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return search_knowledge(
            query=match.group(1).strip(),
            current_evidence=current_evidence,
        )
    
    match = re.fullmatch(r"ask_user\[(.+)]", action, flags=re.IGNORECASE)
    if match:
        question = match.group(1).strip()
        return f"USER_INPUT_REQUIRED: {question}"

    match = re.fullmatch(r"finish\[(.+)]", action, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return f"FINISH: {match.group(1).strip()}"

    return (
        "ERROR: Unknown or malformed action. "
        "Use one action exactly as listed in the system prompt."
    )


def parse_response(response: str) -> tuple[str, str]:
    """Extract exactly one Thought and one Action from the model response."""

    response = response.strip()

    pattern = re.compile(
        r"^Thought:\s*(.+?)\n"
        r"Action:\s*(.+)$",
        flags=re.IGNORECASE | re.DOTALL,
    )

    match = pattern.fullmatch(response)

    if not match:
        raise ValueError(
            "Model response must contain exactly one Thought and one Action.\n"
            f"Received:\n{response}"
        )

    thought = match.group(1).strip()
    action = match.group(2).strip()

    # Reject model-generated ReAct steps after the first action.
    forbidden_markers = (
        "\nObservation:",
        "\nThought:",
        "\nAction:",
    )

    if any(marker.lower() in action.lower() for marker in forbidden_markers):
        raise ValueError(
            "Model generated extra ReAct steps instead of waiting "
            "for the tool observation."
        )

    return thought, action


def investigate(
    incident_request: str,
    generate: GenerateFunction,
    max_steps: int = 6,
) -> str:
    """
    Run the ReAct investigation loop.

    The accumulated trace acts as short-term working memory for this run.
    """
    trace = ""
    evidence_trace = f"Current user request:\n{incident_request}\n\n"
    has_incident_details = False
    has_log_evidence = False
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "===== CURRENT USER REQUEST =====\n"
        f"{incident_request}\n"
        "===== END CURRENT USER REQUEST =====\n\n"
        "Use all concrete values in the current user request, including any "
        "incident ID. Do not ask for information already provided.\n\n"
    )

    MAX_FORMAT_RETRIES = 3

    for step in range(1, max_steps + 1):
        correction = ""

        for attempt in range(1, MAX_FORMAT_RETRIES + 1):

                response = generate(
                    prompt
                    + trace
                    + correction
                )

                print("\n===== RAW MODEL RESPONSE =====")
                print(repr(response))
                print("===== END RAW MODEL RESPONSE =====")

                try:
                    thought, action = parse_response(response)
                    break

                except ValueError as exc:
                    print(
                        f"\nInvalid model response "
                        f"(attempt {attempt}/{MAX_FORMAT_RETRIES}): {exc}"
                    )

                    if attempt == MAX_FORMAT_RETRIES:
                        raise RuntimeError(
                            "Model failed to produce a valid Thought/Action "
                            f"response after {MAX_FORMAT_RETRIES} attempts."
                        ) from exc

                    correction = (
                        "\n\nSYSTEM CORRECTION:\n"
                        "Your previous response violated the required ReAct protocol.\n"
                        "Output exactly one Thought and one Action.\n"
                        "Do not generate an Observation.\n"
                        "Do not generate another Thought or Action.\n"
                        "Stop immediately after the Action.\n"
                    )

       

        print("\n===== PARSED ACTION =====")
        print(repr(action))
        print("===== END PARSED ACTION =====")

        if re.fullmatch(r"finish\[.+]", action, flags=re.IGNORECASE | re.DOTALL):
         missing_evidence = []
         if not has_incident_details:
                missing_evidence.append("incident details")

         if not has_log_evidence:
                missing_evidence.append("direct log evidence")

         if missing_evidence:
                observation = (
                    "GUARDRAIL_BLOCKED: Cannot finish the investigation yet. "
                    "Missing required evidence: "
                    + ", ".join(missing_evidence)
                    + ". Continue investigating."
                )
         else:
                observation = execute_action(
                    action,
                    current_evidence=evidence_trace,
                )
        else:
            observation = execute_action(
                action,
                current_evidence=evidence_trace,
            )

        print("\n===== TOOL OBSERVATION =====")
        print(repr(observation))
        print("===== END TOOL OBSERVATION =====")

        print(f"\nStep {step}")
        print(f"Thought: {thought}")
        print(f"Action: {action}")
        print(f"Observation: {observation}")

        if (re.fullmatch(r"get_incident_details\[.+]",
        action,
        flags=re.IGNORECASE | re.DOTALL,
        )
            and not observation.startswith("ERROR:")
            and "No incident found" not in observation
        ):
            has_incident_details = True

        if (
            re.fullmatch(
                r"search_logs\[.+]",
                action,
                flags=re.IGNORECASE | re.DOTALL,
            )
            and not observation.startswith("ERROR:")
            and not observation.startswith("No log search query was provided.")
            and not observation.startswith("No log entries matched")
            and observation.strip()
        ):
         has_log_evidence = True

        if observation.startswith("FINISH:"):
            return observation.removeprefix("FINISH:").strip()

        if observation.startswith("USER_INPUT_REQUIRED:"):
            return observation

        evidence_trace += (
                f"Action: {action}\n"
                f"Observation: {observation}\n\n"
            )

        trace += (
            f"Thought: {thought}\n"
            f"Action: {action}\n"
            f"Observation: {observation}\n\n"
        )

    return (
        "Investigation stopped because the maximum number of reasoning "
        "steps was reached."
    )
