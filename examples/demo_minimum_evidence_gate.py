from src.agent import investigate


def fake_generate_factory(responses):
    responses = iter(responses)

    def fake_generate(_prompt: str) -> str:
        return next(responses)

    return fake_generate


print("\n=== TEST 1: finish immediately ===")

result = investigate(
    "Investigate incident INC-001.",
    generate=fake_generate_factory(
        [
            (
                "Thought: I already know enough.\n"
                "Action: finish[The deployment caused the incident.]"
            ),
            (
                "Thought: I need the incident details first.\n"
                "Action: get_incident_details[INC-001]"
            ),
            (
                "Thought: I now need direct log evidence.\n"
                "Action: search_logs[payment-service]"
            ),
            (
                "Thought: I now have the minimum required evidence.\n"
                "Action: finish[Investigation completed with incident details and direct log evidence.]"
            ),
        ]
    ),
)

print("\nFINAL RESULT:")
print(result)