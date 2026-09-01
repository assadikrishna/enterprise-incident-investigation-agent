from .llm import generate

ALLOWED_CLASSIFICATIONS = {
    "SUPPORTING",
    "ALTERNATIVE",
    "CONTRADICTORY",
    "REJECT",
}


def validate_classification(classification: str) -> str:
    classification = classification.strip().upper()

    if classification not in ALLOWED_CLASSIFICATIONS:
        raise ValueError(
            f"Invalid classification: {classification}"
        )

    return classification


VERIFICATION_PROMPT = """
You are an evidence-consistency verifier for an incident investigation.

Compare the current incident evidence with the retrieved document.

Classify the retrieved document as exactly one of:

SUPPORTING
- The document provides evidence or guidance consistent with the current incident evidence.

ALTERNATIVE
- The document describes a different plausible causal explanation
  for the same or closely related symptoms in the current incident.
- There must be a meaningful causal connection to the current evidence.

CONTRADICTORY
- The document directly conflicts with the current incident evidence
  or hypothesis.

REJECT
- The document is not useful enough for this investigation.
- Choose REJECT when the document discusses a different primary symptom,
  unrelated failure mode, or only generic information without a meaningful
  causal connection to the current incident evidence.

Do not classify a document as ALTERNATIVE merely because it describes
a general way that a service could fail.

Return exactly one line in this format:

Classification: <LABEL>

Do not invent facts.
Do not determine the root cause.
Use only the current evidence and retrieved document provided.
"""

def verify_retrieved_evidence(
    current_evidence: str,
    retrieved_document: str,
) -> str:
    prompt = f"""
{VERIFICATION_PROMPT}

Current incident evidence:
{current_evidence}

Retrieved document:
{retrieved_document}
"""

    response = generate(prompt)

    if not response.startswith("Classification:"):
        raise ValueError(
            f"Invalid verifier response format: {response}"
        )

    classification = response.split(":", 1)[1]

    return validate_classification(classification)