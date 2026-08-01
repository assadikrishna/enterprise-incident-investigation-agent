from src.agent import investigate

responses = iter(
    [
        "Thought: I should first retrieve the incident record.\n"
        "Action: get_incident_details[INC-001]",

        "Thought: The incident followed a deployment, so I should inspect payment-service logs.\n"
        "Action: search_logs[payment-service]",

        "Thought: The logs show database connection pool exhaustion. I should check the service runbook.\n"
        "Action: get_runbook[payment-service]",

        "Thought: I now have enough evidence for an initial recommendation.\n"
        "Action: finish[The payment service is returning HTTP 503 responses. "
        "The strongest evidence points to database connection-pool exhaustion "
        "after the recent deployment. The engineer should verify pool settings, "
        "database health, and deployment configuration before approving any "
        "rollback, restart, or scaling action.]",
    ]
)


def fake_generate(_: str) -> str:
    return next(responses)


result = investigate(
    "Investigate incident INC-001.",
    generate=fake_generate,
)

print("\nFinal result:")
print(result)