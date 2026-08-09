from src.retrieval import SemanticRetriever


def main() -> None:
    retriever = SemanticRetriever()

    query = (
        "Payment service is returning HTTP 503 errors "
        "and database connections are timing out after deployment."
    )

    results = retriever.search(query, top_k=3)

    print(f"\nQuery:\n{query}\n")

    print("Retrieved context:")

    for rank, result in enumerate(results, start=1):
        print(f"\n--- Result {rank} ---")
        print(f"Source: {result['source']}")
        print(f"Score: {result['score']:.4f}")
        print(result["text"])


if __name__ == "__main__":
    main()