
import re
from rank_bm25 import BM25Okapi

from backend.rag.registry import document_registry


class SparseRetriever:

    def __init__(self):
        self.bm25 = None
        self.chunks = []

    @staticmethod
    def tokenize(text):
        return re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

    def build_index(self, chunks=None):

        self.chunks = (
            chunks if chunks is not None
            else document_registry.get_all_chunks()
        )

        if not self.chunks:
            self.bm25 = None
            return

        corpus = [
            self.tokenize(item["text"])
            for item in self.chunks
        ]

        self.bm25 = BM25Okapi(corpus)

    def search(self, query, top_k=5, filters=None):

        if self.bm25 is None:
            self.build_index()

        if self.bm25 is None:
            return []

        scores = self.bm25.get_scores(
            self.tokenize(query)
        )

        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True
        )

        results = []

        for index, score in ranked:

            if score <= 0:
                continue

            chunk = self.chunks[index]
            metadata = chunk.get("metadata", {})

            if filters and any(
                metadata.get(key) != value
                for key, value in filters.items()
            ):
                continue

            results.append({
                "id": chunk["id"],
                "text": chunk["text"],
                "metadata": metadata,
                "score": float(score),
                "retrieval_method": "sparse"
            })

            if len(results) >= top_k:
                break

        return results


sparse_retriever = SparseRetriever()
