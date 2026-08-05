from src.agent import investigate
from src.llm import generate


def main() -> None:
    result = investigate(
        incident_request="Investigate incident INC-001.",
        generate=generate,
        max_steps=6,
    )

    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    main()