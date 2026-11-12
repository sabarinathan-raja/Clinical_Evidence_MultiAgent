
from backend.core.config import settings
from backend.rag.dense_retrieval import dense_retriever
from backend.rag.sparse_retrieval import sparse_retriever


class HybridRetriever:

    def __init__(self, rrf_k=60):
        self.dense = dense_retriever
        self.sparse = sparse_retriever
        self.rrf_k = rrf_k

    def search(
        self,
        query,
        top_k=None,
        filters=None
    ):

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        limit = top_k or settings.TOP_K

        dense_results = self.dense.search(
            query,
            top_k=limit * 2,
            filters=filters
        )

        sparse_results = self.sparse.search(
            query,
            top_k=limit * 2,
            filters=filters
        )

        combined = {}

        for results in (dense_results, sparse_results):

            for rank, item in enumerate(results, start=1):

                key = item["id"]

                if key not in combined:
                    combined[key] = {
                        **item,
                        "rrf_score": 0.0,
                        "retrieval_methods": []
                    }

                combined[key]["rrf_score"] += (
                    1.0 / (self.rrf_k + rank)
                )

                combined[key]["retrieval_methods"].append(
                    item["retrieval_method"]
                )

        ranked = sorted(
            combined.values(),
            key=lambda item: item["rrf_score"],
            reverse=True
        )

        for item in ranked:
            item["score"] = item["rrf_score"]

        return ranked[:limit]


hybrid_retriever = HybridRetriever()
