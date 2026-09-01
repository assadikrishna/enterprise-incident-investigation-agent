from src.tools import search_knowledge


current_evidence = """
Current user request:
Investigate INC-001.

Action: get_incident_details[INC-001]
Observation:
service: payment-service
severity: high
summary: Users receive HTTP 503 errors after deployment.
recent_change: payment-service version 2.3 deployed at 10:00

Action: search_logs[payment-service]
Observation:
10:02 | payment-service | HTTP 503 returned by payment-service
10:02 | payment-service | Database connection pool exhausted
10:03 | payment-service | Retry attempt failed after database timeout
"""

result = search_knowledge(
    query="high CPU performance issue",
    current_evidence=current_evidence,
)

print(result)