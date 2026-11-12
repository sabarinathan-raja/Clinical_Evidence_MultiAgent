
import re


class DeidentificationService:

    PATTERNS = {
        "email": (
            r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b",
            "[REDACTED_EMAIL]"
        ),
        "phone": (
            r"\b(?:\+?\d{1,3}[- ]?)?\d{10}\b",
            "[REDACTED_PHONE]"
        ),
        "date": (
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            "[REDACTED_DATE]"
        ),
        "mrn": (
            r"\b(?:MRN|Patient ID)\s*[:#-]?\s*[A-Za-z0-9-]+",
            "[REDACTED_ID]"
        ),
        "aadhaar": (
            r"\b\d{4}\s?\d{4}\s?\d{4}\b",
            "[REDACTED_ID]"
        )
    }

    def deidentify(self, text: str) -> dict:

        if not text:
            return {
                "text": text,
                "redactions": 0,
                "is_deidentified": True
            }

        redactions = 0

        for name, (pattern, replacement) in self.PATTERNS.items():

            text, count = re.subn(
                pattern,
                replacement,
                text,
                flags=re.IGNORECASE
            )

            redactions += count

        return {
            "text": text,
            "redactions": redactions,
            "is_deidentified": True
        }


deidentification_service = DeidentificationService()
