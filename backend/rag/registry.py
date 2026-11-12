
from threading import RLock


class DocumentRegistry:

    def __init__(self):
        self._documents = {}
        self._chunks = {}
        self._lock = RLock()

    def register_document(self, document_id, metadata):
        with self._lock:
            self._documents[document_id] = metadata

    def register_chunks(self, chunks):
        with self._lock:
            for chunk in chunks:
                self._chunks[chunk["id"]] = chunk

    def get_document(self, document_id):
        with self._lock:
            return self._documents.get(document_id)

    def get_chunk(self, chunk_id):
        with self._lock:
            return self._chunks.get(chunk_id)

    def get_all_chunks(self):
        with self._lock:
            return list(self._chunks.values())

    def get_document_chunks(self, document_id):
        with self._lock:
            return [
                item for item in self._chunks.values()
                if item.get("document_id") == document_id
            ]

    def remove_document(self, document_id):
        with self._lock:
            self._documents.pop(document_id, None)

            ids = [
                key for key, value in self._chunks.items()
                if value.get("document_id") == document_id
            ]

            for key in ids:
                self._chunks.pop(key, None)

    def restore_chunks(self, records):
        with self._lock:
            for record in records:
                metadata = record.get("metadata") or {}
                chunk_id = record["id"]

                self._chunks[chunk_id] = {
                    "id": chunk_id,
                    "text": record.get("text", ""),
                    "document_id": metadata.get("document_id"),
                    "metadata": metadata
                }


document_registry = DocumentRegistry()
