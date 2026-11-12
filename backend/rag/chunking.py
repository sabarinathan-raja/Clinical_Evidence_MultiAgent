
from backend.core.config import settings


class TextChunker:

    def __init__(
        self,
        chunk_size=None,
        chunk_overlap=None
    ):

        self.chunk_size = (
            chunk_size or settings.CHUNK_SIZE
        )

        self.chunk_overlap = (
            settings.CHUNK_OVERLAP
            if chunk_overlap is None
            else chunk_overlap
        )

        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be positive.")

        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("Invalid chunk overlap.")

    def split_text(self, text: str) -> list[str]:

        if not text or not text.strip():
            return []

        words = text.split()
        chunks = []

        start = 0

        while start < len(words):

            end = min(
                start + self.chunk_size,
                len(words)
            )

            chunk = " ".join(words[start:end])

            if chunk.strip():
                chunks.append(chunk)

            if end == len(words):
                break

            start = end - self.chunk_overlap

        return chunks

    def split_documents(
        self,
        documents: list[dict]
    ) -> list[dict]:

        results = []

        for document in documents:

            chunks = self.split_text(
                document.get("text", "")
            )

            for index, chunk in enumerate(chunks):

                results.append({
                    "text": chunk,
                    "chunk_index": index,
                    "source": document.get("source", ""),
                    "page": document.get("page"),
                    "file_path": document.get("file_path", "")
                })

        return results
