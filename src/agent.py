from __future__ import annotations

import re
from collections.abc import Callable

from .tools import get_incident_details, get_runbook, search_logs


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
- get_incident_details[incident_id]
- search_logs[query]
- get_runbook[service]
- ask_user[question]
- finish[answer]

Required response format:
Thought: <brief reasoning about the next investigation step>
Action: <one available action>
""".strip()


def execute_action(action: str) -> str:
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
    """Extract Thought and Action fields from the model response."""
    thought_match = re.search(
        r"Thought:\s*(.+?)(?=\nAction:|\Z)",
        response,
        flags=re.IGNORECASE | re.DOTALL,
    )
    action_match = re.search(
        r"Action:\s*(.+)",
        response,
        flags=re.IGNORECASE,
    )

    thought = thought_match.group(1).strip() if thought_match else ""
    action = action_match.group(1).strip() if action_match else ""

    if not action:
        raise ValueError(f"Could not parse an action from model response:\n{response}")

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
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"User request: {incident_request}\n\n"
    )

    for step in range(1, max_steps + 1):
        response = generate(prompt + trace)
        thought, action = parse_response(response)
        observation = execute_action(action)

        print(f"\nStep {step}")
        print(f"Thought: {thought}")
        print(f"Action: {action}")
        print(f"Observation: {observation}")

        if observation.startswith("FINISH:"):
            return observation.removeprefix("FINISH:").strip()

        if observation.startswith("USER_INPUT_REQUIRED:"):
            return observation

        trace += (
            f"Thought: {thought}\n"
            f"Action: {action}\n"
            f"Observation: {observation}\n\n"
        )

    return (
        "Investigation stopped because the maximum number of reasoning "
        "steps was reached."
    )