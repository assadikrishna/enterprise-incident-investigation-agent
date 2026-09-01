from __future__ import annotations

from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

KNOWLEDGE_DIR = Path("data/synthetic/knowledge")

CHUNK_SIZE = 100
TOP_K = 3
MIN_RELEVANCE_SCORE = 0.40


class SemanticRetriever:
    """Semantic retrieval over synthetic incident knowledge."""

    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)
        self.index: faiss.IndexFlatIP | None = None
        self.chunks: list[dict[str, Any]] = []

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = CHUNK_SIZE,
    ) -> list[str]:
        """Split text into fixed-size word chunks."""
        words = text.split()

        return [
            " ".join(words[i : i + chunk_size])
            for i in range(0, len(words), chunk_size)
        ]

    def load_documents(self) -> None:
        """Load and chunk Markdown knowledge documents."""
        chunks: list[dict[str, Any]] = []

        for path in KNOWLEDGE_DIR.rglob("*.md"):
            text = path.read_text(encoding="utf-8")

            for chunk_number, chunk_text in enumerate(
                self._chunk_text(text)
            ):
                chunks.append(
                    {
                        "source": str(path),
                        "chunk_number": chunk_number,
                        "text": chunk_text,
                    }
                )

        if not chunks:
            raise RuntimeError(
                f"No knowledge documents found under {KNOWLEDGE_DIR}."
            )

        self.chunks = chunks

    def build_index(self) -> None:
        """Create embeddings and build a FAISS similarity index."""
        if not self.chunks:
            self.load_documents()

        texts = [chunk["text"] for chunk in self.chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

    def search(
        self,
        query: str,
        top_k: int = TOP_K,
    ) -> list[dict[str, Any]]:
        """Return the most semantically relevant chunks."""
        if not query.strip():
            raise ValueError("Retrieval query cannot be empty.")

        if self.index is None:
            self.build_index()

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, len(self.chunks)),
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            if score < MIN_RELEVANCE_SCORE:
                continue

            result = dict(self.chunks[index])
            result["score"] = float(score)
            results.append(result)

        return results