
from backend.rag.text_cleaner import TextCleaner
from backend.rag.chunking import TextChunker
from backend.rag.context_builder import ContextBuilder
from backend.rag.sparse_retrieval import SparseRetriever
from backend.rag.hybrid_retrieval import HybridRetriever


def test_text_cleaner():

    result = TextCleaner.clean(
        "Clinical   Evidence\n\n\nResearch"
    )

    assert "Clinical Evidence" in result
    assert "\n\n\n" not in result


def test_text_chunker():

    chunker = TextChunker(
        chunk_size=3,
        chunk_overlap=1
    )

    result = chunker.split_text(
        "one two three four five six"
    )

    assert len(result) > 1


def test_empty_chunking():

    chunker = TextChunker()

    assert chunker.split_text("") == []


def test_context_builder():

    builder = ContextBuilder()

    result = builder.build(
        query="clinical evidence",
        documents=[
            {
                "id": "chunk1",
                "text": "Synthetic clinical research evidence",
                "metadata": {
                    "source": "test.pdf",
                    "page": 1
                }
            }
        ]
    )

    assert result["evidence_count"] == 1
    assert result["is_empty"] is False
    assert result["citations"][0]["citation_id"] == "E1"


def test_sparse_retrieval():

    retriever = SparseRetriever()

    chunks = [
        {
            "id": "1",
            "text": "diabetes clinical evidence research",
            "metadata": {"source": "a.pdf"}
        },
        {
            "id": "2",
            "text": "cardiology research evidence",
            "metadata": {"source": "b.pdf"}
        }
    ]

    retriever.build_index(chunks)

    results = retriever.search(
        "diabetes evidence",
        top_k=2
    )

    assert len(results) >= 1
    assert results[0]["id"] == "1"


def test_hybrid_retrieval(monkeypatch):

    class FakeRetriever:

        def __init__(self, method):
            self.method = method

        def search(self, query, top_k=None, filters=None):

            return [
                {
                    "id": "1",
                    "text": "Synthetic evidence",
                    "metadata": {},
                    "score": 0.9,
                    "retrieval_method": self.method
                }
            ]

    retriever = HybridRetriever()

    retriever.dense = FakeRetriever("dense")
    retriever.sparse = FakeRetriever("sparse")

    results = retriever.search(
        "clinical evidence",
        top_k=2
    )

    assert len(results) == 1
    assert len(results[0]["retrieval_methods"]) == 2
