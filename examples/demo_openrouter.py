import time
from src.agent import investigate
from src.llm import generate


def main() -> None:
    start_time = time.perf_counter()
    result = investigate(
        incident_request="Investigate incident INC-001.",
        generate=generate,
        max_steps=6,
    )
    elapsed_time = time.perf_counter() - start_time

    print("\nFinal result:")
    print(result)
    print(f"\nExecution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()