
import chromadb

from backend.core.config import settings
from backend.rag.embeddings import EmbeddingService


class DenseRetriever:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.client = None
        self.collection = None

    def initialize(self):

        if self.collection is not None:
            return self.collection

        settings.chroma_path.mkdir(
            parents=True, exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_path)
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        return self.collection

    def add_documents(self, ids, texts, metadatas):

        if not ids:
            return

        collection = self.initialize()

        vectors = self.embedding_service.embed_documents(
            texts
        )

        collection.upsert(
            ids=ids,
            embeddings=vectors,
            documents=texts,
            metadatas=metadatas
        )

    def search(self, query, top_k=None, filters=None):

        collection = self.initialize()
        count = collection.count()

        if count == 0:
            return []

        vector = self.embedding_service.embed_query(query)

        arguments = {
            "query_embeddings": [vector],
            "n_results": min(top_k or settings.TOP_K, count),
            "include": [
                "documents", "metadatas", "distances"
            ]
        }

        if filters:
            arguments["where"] = filters

        results = collection.query(**arguments)

        output = []

        ids = results.get("ids", [[]])[0]
        texts = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i, chunk_id in enumerate(ids):

            output.append({
                "id": chunk_id,
                "text": texts[i],
                "metadata": metas[i] or {},
                "score": max(0.0, 1.0 - float(distances[i])),
                "retrieval_method": "dense"
            })

        return output

    def delete_document(self, document_id):

        collection = self.initialize()

        collection.delete(
            where={"document_id": document_id}
        )


dense_retriever = DenseRetriever()
