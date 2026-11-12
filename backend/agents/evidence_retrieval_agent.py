
import logging

from backend.rag.hybrid_retrieval import hybrid_retriever
from backend.rag.reranker import evidence_reranker
from backend.rag.context_builder import context_builder

logger = logging.getLogger(__name__)


class EvidenceRetrievalAgent:

    def run(self, query: str, top_k: int = 5) -> dict:

        if not query or not query.strip():
            raise ValueError(
                "Evidence retrieval query is required."
            )

        retrieved = hybrid_retriever.search(
            query=query,
            top_k=top_k * 2
        )

        if not retrieved:

            return {
                "query": query,
                "evidence": [],
                "citations": [],
                "context": "",
                "evidence_count": 0,
                "warnings": [
                    "No matching evidence found in indexed documents."
                ]
            }

        ranked = evidence_reranker.rerank(
            query=query,
            documents=retrieved,
            top_k=top_k
        )

        context = context_builder.build(
            query=query,
            documents=ranked
        )

        evidence = []

        for item in ranked:

            metadata = item.get("metadata", {})

            evidence.append({
                "id": item["id"],
                "title": metadata.get(
                    "title",
                    metadata.get("source", "Untitled")
                ),
                "content": item["text"],
                "source": metadata.get("source", ""),
                "page": metadata.get("page"),
                "evidence_type": metadata.get(
                    "evidence_type", "unknown"
                ),
                "relevance_score": item.get(
                    "rerank_score"
                ),
                "retrieval_methods": item.get(
                    "retrieval_methods", []
                )
            })

        return {
            "query": query,
            "evidence": evidence,
            "citations": context["citations"],
            "context": context["context"],
            "evidence_count": len(evidence),
            "warnings": []
        }


evidence_retrieval_agent = EvidenceRetrievalAgent()
