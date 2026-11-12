
import re


class PromptInjectionDetector:

    PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"reveal\s+(the\s+)?system\s+prompt",
        r"disregard\s+(all\s+)?rules",
        r"act\s+as\s+an?\s+unrestricted",
        r"bypass\s+(the\s+)?safety",
        r"developer\s+message\s*:",
        r"system\s+prompt\s*:"
    ]

    def inspect(self, text: str) -> dict:

        detected = []

        for pattern in self.PATTERNS:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            ):
                detected.append(pattern)

        return {
            "is_suspicious": bool(detected),
            "detected_patterns": detected,
            "action": (
                "flag_for_review"
                if detected
                else "continue_with_untrusted_input"
            )
        }


prompt_injection_detector = PromptInjectionDetector()
