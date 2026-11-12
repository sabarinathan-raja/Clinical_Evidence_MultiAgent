
from backend.core.config import settings


class EvidenceReranker:

    def __init__(self):
        self.model = None

    def _load_model(self):

        if self.model is None:

            from sentence_transformers import CrossEncoder

            self.model = CrossEncoder(
                settings.RERANKER_MODEL
            )

        return self.model

    def rerank(self, query, documents, top_k=None):

        if not documents:
            return []

        model = self._load_model()

        pairs = [
            [query, item["text"]]
            for item in documents
        ]

        scores = model.predict(
            pairs,
            show_progress_bar=False
        )

        results = []

        for item, score in zip(documents, scores):

            result = dict(item)
            result["rerank_score"] = float(score)

            results.append(result)

        results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        return results[
            :top_k or settings.RERANK_TOP_K
        ]


evidence_reranker = EvidenceReranker()
