
import hashlib
import uuid
from pathlib import Path

from backend.rag.pdf_loader import PDFLoader, load_text_file
from backend.rag.text_cleaner import TextCleaner
from backend.rag.chunking import TextChunker
from backend.rag.dense_retrieval import dense_retriever
from backend.rag.sparse_retrieval import sparse_retriever
from backend.rag.registry import document_registry


class DocumentIngestionService:

    def __init__(self):

        self.pdf_loader = PDFLoader()
        self.cleaner = TextCleaner()
        self.chunker = TextChunker()

    def ingest(
        self,
        file_path: str,
        document_id: str = None
    ) -> dict:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(file_path)

        extension = path.suffix.lower()

        if extension == ".pdf":
            pages = self.pdf_loader.load(file_path)

        elif extension in {".txt", ".md"}:
            pages = load_text_file(file_path)

        else:
            raise ValueError(
                f"Unsupported file extension: {extension}"
            )

        document_id = document_id or str(uuid.uuid4())

        all_chunks = []

        for page in pages:

            cleaned = self.cleaner.clean(
                page["text"]
            )

            page["text"] = cleaned

        chunks = self.chunker.split_documents(
            pages
        )

        if not chunks:
            raise ValueError("No usable text chunks found.")

        file_hash = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        ids = []
        texts = []
        metadatas = []

        registry_chunks = []

        for index, chunk in enumerate(chunks):

            chunk_id = str(uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"{document_id}:{index}"
            ))

            metadata = {
                "document_id": document_id,
                "source": path.name,
                "page": chunk["page"] or 0,
                "chunk_index": index,
                "file_hash": file_hash
            }

            ids.append(chunk_id)
            texts.append(chunk["text"])
            metadatas.append(metadata)

            registry_chunks.append({
                "id": chunk_id,
                "text": chunk["text"],
                "document_id": document_id,
                "metadata": metadata
            })

        dense_retriever.add_documents(
            ids=ids,
            texts=texts,
            metadatas=metadatas
        )

        document_registry.register_document(
            document_id,
            {
                "filename": path.name,
                "file_path": str(path),
                "checksum": file_hash,
                "chunk_count": len(chunks)
            }
        )

        document_registry.register_chunks(
            registry_chunks
        )

        sparse_retriever.build_index()

        return {
            "success": True,
            "document_id": document_id,
            "filename": path.name,
            "checksum": file_hash,
            "pages_processed": len(pages),
            "chunks_created": len(chunks),
            "message": "Document ingestion completed."
        }


ingestion_service = DocumentIngestionService()
