from src.verification import verify_retrieved_evidence


current_evidence = """
Service: payment-service
Observed symptoms:
- HTTP 503 errors
- Database connection pool exhausted
- Retry failed after database timeout
Recent change:
- Version 2.3 deployed shortly before the incident
"""


inc_101 = """
Historical incident INC-101:
The payment service returned HTTP 503 errors after a deployment.
Investigation found database connection pool exhaustion.
The incident was resolved after an engineer reviewed and restored
the previous connection pool configuration.
"""


inc_103 = """
Historical incident INC-103:
The payment service returned HTTP 503 errors because a downstream
dependency was timing out.
Database connectivity and connection pool utilization remained normal.
"""

kb_cpu = """
Knowledge Base:
High CPU utilization may cause degraded response times or request failures.
Common causes include inefficient code, excessive request volume,
runaway background jobs, garbage collection overhead, or low resource limits.
"""


print("INC-101:")
print(
    verify_retrieved_evidence(
        current_evidence,
        inc_101,
    )
)

print()

print("INC-103:")
print(
    verify_retrieved_evidence(
        current_evidence,
        inc_103,
    )
)

print()

print("KB CPU:")
print(
    verify_retrieved_evidence(
        current_evidence,
        kb_cpu,
    )
)