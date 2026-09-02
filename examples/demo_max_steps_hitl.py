from src.agent import investigate


def fake_generate_factory(responses):
    responses = iter(responses)

    def fake_generate(_prompt: str) -> str:
        return next(responses)

    return fake_generate


result = investigate(
    "Investigate incident INC-001.",
    generate=fake_generate_factory(
        [
            (
                "Thought: I need the incident details.\n"
                "Action: get_incident_details[INC-001]"
            ),
            (
                "Thought: I need direct log evidence.\n"
                "Action: search_logs[payment-service]"
            ),
            (
                "Thought: I should inspect the runbook.\n"
                "Action: get_runbook[payment-service]"
            ),
            (
                "Thought: I want more log evidence.\n"
                "Action: search_logs[payment-service]"
            ),
            (
                "Thought: I still want more evidence.\n"
                "Action: search_logs[payment-service]"
            ),
            (
                "Thought: I will continue investigating.\n"
                "Action: search_logs[payment-service]"
            ),
        ]
    ),
)

print("\nFINAL RESULT:")
print(result)