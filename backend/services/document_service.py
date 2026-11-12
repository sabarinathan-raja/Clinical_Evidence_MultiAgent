from __future__ import annotations

from pathlib import Path

from backend.rag.ingestion import ingest_file, ingest_seed_documents
from backend.rag.registry import read_registry


def ingest_path(path: Path) -> dict:
    return ingest_file(path)


def list_documents() -> list[dict]:
    ingest_seed_documents()
    return [{key: item[key] for key in ("document_id", "title", "source_path")} | {"chunks_indexed": len(item["chunks"])} for item in read_registry()]
