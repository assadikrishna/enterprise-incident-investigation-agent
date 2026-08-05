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
- get_incident_details[<incident_id>]
- search_logs[<query>]
- get_runbook[<service>]
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
        flags=re.IGNORECASE | re.DOTALL,
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
        "===== CURRENT USER REQUEST =====\n"
        f"{incident_request}\n"
        "===== END CURRENT USER REQUEST =====\n\n"
        "Use all concrete values in the current user request, including any "
        "incident ID. Do not ask for information already provided.\n\n"
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
