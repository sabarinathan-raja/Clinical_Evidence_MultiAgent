
from functools import lru_cache

from backend.core.config import settings


class EmbeddingService:

    def __init__(self, model_name=None):

        self.model_name = (
            model_name or settings.EMBEDDING_MODEL
        )

        self._model = None

    def _load_model(self):

        if self._model is None:

            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self.model_name
            )

        return self._model

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        if not texts:
            return []

        model = self._load_model()

        vectors = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:

        if not text or not text.strip():
            raise ValueError("Query cannot be empty.")

        model = self._load_model()

        vector = model.encode(
            text,
            normalize_embeddings=True
        )

        return vector.tolist()

    def health_check(self):

        return {
            "model": self.model_name,
            "loaded": self._model is not None
        }
