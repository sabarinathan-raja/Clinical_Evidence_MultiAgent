from __future__ import annotations

from backend.rag.hybrid_retrieval import hybrid_search
from backend.rag.ingestion import ingest_seed_documents


def search_evidence(query: str) -> list[dict]:
    ingest_seed_documents()
    return hybrid_search(query)
