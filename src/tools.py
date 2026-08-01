from __future__ import annotations

from typing import Any


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
    """Search synthetic logs using simple case-insensitive matching."""
    normalized_query = query.strip().lower()

    matches = [
        log
        for log in LOGS
        if normalized_query in log["service"].lower()
        or normalized_query in log["message"].lower()
    ]

    if not matches:
        return f"No log entries matched '{query}'."

    return "\n".join(
        f'{log["timestamp"]} | {log["service"]} | {log["message"]}'
        for log in matches
    )


def get_runbook(service: str) -> str:
    """Return the synthetic runbook for a service."""
    return RUNBOOKS.get(service, f"No runbook found for {service}.")