
from pathlib import Path


class PDFLoader:

    def load(self, file_path: str) -> list[dict]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(file_path)

        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")

        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = []

        for index, page in enumerate(reader.pages):

            text = page.extract_text() or ""

            if text.strip():
                pages.append({
                    "page": index + 1,
                    "text": text,
                    "source": path.name,
                    "file_path": str(path)
                })

        if not pages:
            raise ValueError(
                "No extractable text found in PDF. "
                "OCR may be required for scanned documents."
            )

        return pages


def load_text_file(file_path: str) -> list[dict]:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(file_path)

    text = path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    return [{
        "page": 1,
        "text": text,
        "source": path.name,
        "file_path": str(path)
    }]
