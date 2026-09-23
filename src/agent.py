from __future__ import annotations

import re
from collections.abc import Callable

from .protocol import SYSTEM_PROMPT, parse_response
from .tools import get_incident_details, get_runbook, search_logs, search_knowledge


GenerateFunction = Callable[[str], str]

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


def investigate(
    incident_request: str,
    generate: GenerateFunction,
    max_steps: int = 6,
    debug: bool = False,
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
                if debug:
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

       
        if debug:
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
    
        if debug:
            print("\n===== TOOL OBSERVATION =====")
            print(repr(observation))
            print("===== END TOOL OBSERVATION =====")

        if observation.startswith("FINISH:"):
            print(f"\nStep {step}")
            print("Action: Complete investigation")
        else:
            print(f"\nStep {step}")
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            display_observation = format_observation_for_display(action, observation)
            print(f"Observation: {display_observation}")
       

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

        if (
            not observation.startswith("GUARDRAIL_BLOCKED:")
            and not observation.startswith("ERROR:")
        ):
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
        "HUMAN_INPUT_REQUIRED: The investigation reached the maximum "
        "number of reasoning steps without reaching a sufficiently supported "
        "conclusion.\n\n"
        "Verified evidence collected so far:\n"
        f"{evidence_trace}\n"
        "Recommended human action: Review the verified evidence above and "
        "provide additional incident context or investigate information that "
        "the current tools cannot access."
    )


def format_observation_for_display(action: str, observation: str) -> str:
    if action.lower().startswith("search_knowledge["):
        results = observation.split("\n\n---\n\n")
        lines = []

        for result in results:
            source = ""
            score = ""
            classification = ""

            for line in result.splitlines():
                if line.startswith("Source:"):
                    source = line.removeprefix("Source:").strip()
                elif line.startswith("Score:"):
                    score = line.removeprefix("Score:").strip()
                elif line.startswith("Classification:"):
                    classification = line.removeprefix("Classification:").strip()

            if source:
                source = source.replace("\\", "/").split("/")[-1]

            if source and score and classification:
                lines.append(
                    f"- {source} | Score: {score} | {classification}"
                )

        return "\n".join(lines)

    return observation
