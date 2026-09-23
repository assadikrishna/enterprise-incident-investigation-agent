
from typing import TypedDict


class InvestigationState(TypedDict):
    """Shared state for one incident investigation."""

    incident_request: str

    trace: str
    evidence_trace: str

    thought: str
    action: str
    observation: str

    step: int
    max_steps: int

    has_incident_details: bool
    has_log_evidence: bool

    status: str
    final_answer: str