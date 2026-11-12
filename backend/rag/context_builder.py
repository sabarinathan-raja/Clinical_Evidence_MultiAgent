
class ContextBuilder:

    def __init__(self, max_context_chars=18000):
        self.max_context_chars = max_context_chars

    def build(self, query, documents):

        sections = []
        citations = []
        used_chars = 0

        for index, item in enumerate(documents, start=1):

            metadata = item.get("metadata", {})
            text = item.get("text", "")

            if not text:
                continue

            remaining = (
                self.max_context_chars - used_chars
            )

            if remaining <= 0:
                break

            text = text[:remaining]

            citation_id = f"E{index}"

            source = metadata.get(
                "source", "Unknown source"
            )

            page = metadata.get("page", "N/A")

            sections.append(
                f"[{citation_id}]\n"
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Evidence: {text}"
            )

            citations.append({
                "citation_id": citation_id,
                "chunk_id": item.get("id"),
                "source": source,
                "page": page,
                "evidence_type": metadata.get(
                    "evidence_type", "unknown"
                )
            })

            used_chars += len(text)

        return {
            "query": query,
            "context": "\n\n".join(sections),
            "citations": citations,
            "evidence_count": len(citations),
            "is_empty": len(citations) == 0,
            "context_length": used_chars
        }


context_builder = ContextBuilder()
