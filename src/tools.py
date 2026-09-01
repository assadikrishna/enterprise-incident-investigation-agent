from __future__ import annotations

from typing import Any
from .verification import verify_retrieved_evidence
from .retrieval import SemanticRetriever
_knowledge_retriever = SemanticRetriever()

INCIDENTS: dict[str, dict[str, Any]] = {
    "INC-001": {
        "service": "payment-service",
        "severity": "high",
        "summary": "Users receive HTTP 503 errors after deployment.",
        "recent_change": "payment-service version 2.3 deployed at 10:00",
    }
}

LOGS: list[dict[str, str]] = [
    {
        "service": "payment-service",
        "timestamp": "10:02",
        "message": "HTTP 503 returned by payment-service",
    },
    {
        "service": "payment-service",
        "timestamp": "10:02",
        "message": "Database connection pool exhausted",
    },
    {
        "service": "payment-service",
        "timestamp": "10:03",
        "message": "Retry attempt failed after database timeout",
    },
]

RUNBOOKS: dict[str, str] = {
    "payment-service": (
        "For HTTP 503 errors, inspect dependency health, database connectivity, "
        "connection-pool utilization, and recent deployment changes. "
        "Production changes require engineer approval."
    )
}


def get_incident_details(incident_id: str) -> str:
    """Return details for a synthetic incident."""
    incident = INCIDENTS.get(incident_id)
    if incident is None:
        return f"No incident found for {incident_id}."

    return "\n".join(f"{key}: {value}" for key, value in incident.items())


def search_logs(query: str) -> str:
    """Search synthetic logs using case-insensitive keyword matching."""
    keywords = query.strip().lower().split()

    if not keywords:
        return "No log search query was provided."

    matches = []

    for log in LOGS:
        searchable_text = (
            f'{log["timestamp"]} '
            f'{log["service"]} '
            f'{log["message"]}'
        ).lower()

        if any(keyword in searchable_text for keyword in keywords):
            matches.append(log)

    if not matches:
        return f"No log entries matched '{query}'."

    return "\n".join(
        f'{log["timestamp"]} | {log["service"]} | {log["message"]}'
        for log in matches
    )


def get_runbook(service: str) -> str:
    """Return the synthetic runbook for a service."""
    return RUNBOOKS.get(service, f"No runbook found for {service}.")


def search_knowledge(query: str, current_evidence: str) -> str:
    results = _knowledge_retriever.search(query, top_k=3)

    if not results:
        return "No relevant knowledge found"

    formatted_results = []

    for result in results:
        classification = verify_retrieved_evidence(
            current_evidence=current_evidence,
            retrieved_document=result["text"],
        )

        formatted_results.append(
            f"Source: {result['source']}\n"
            f"Score: {result['score']:.4f}\n"
            f"Classification: {classification}\n"
            f"Content: {result['text']}"
        )

    return "\n\n---\n\n".join(formatted_results)