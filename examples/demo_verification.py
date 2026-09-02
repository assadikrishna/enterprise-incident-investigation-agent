from src.verification import verify_retrieved_evidence_batch


current_evidence = """
Incident INC-001 involves payment-service.
The service returned HTTP 503 errors after deployment.
Logs show database connection pool exhaustion and database timeout.
"""

retrieved_documents = [
    """
    Historical incident INC-101:
    payment-service returned HTTP 503 errors after a deployment.
    Investigation found database connection pool exhaustion.
    A configuration change had reduced the maximum connection pool size.
    Restoring the previous configuration resolved the issue after engineer approval.
    """,
    """
    Historical incident INC-103:
    payment-service returned HTTP 503 errors because a downstream dependency timed out.
    Database connectivity and connection pool utilization were normal.
    """,
    """
    Knowledge article:
    High CPU utilization can cause application performance degradation.
    Check CPU utilization, thread usage, and resource limits.
    """,
]

classifications = verify_retrieved_evidence_batch(
    current_evidence=current_evidence,
    retrieved_documents=retrieved_documents,
)

for index, classification in enumerate(classifications, start=1):
    print(f"Document {index}: {classification}")