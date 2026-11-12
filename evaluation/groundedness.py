
import re


def normalize(text):

    return set(
        re.findall(
            r"\b[a-zA-Z0-9]+\b",
            (text or "").lower()
        )
    )


def evaluate_groundedness(
    answer,
    evidence_context
):

    answer_tokens = normalize(answer)
    evidence_tokens = normalize(evidence_context)

    if not answer_tokens:
        return {
            "score": 0.0,
            "grounded": False,
            "message": "Answer is empty."
        }

    if not evidence_tokens:
        return {
            "score": 0.0,
            "grounded": False,
            "message": "No evidence context available."
        }

    overlap = (
        len(answer_tokens & evidence_tokens)
        / len(answer_tokens)
    )

    return {
        "score": round(overlap, 4),
        "grounded": overlap >= 0.5,
        "message": (
            "Lexical overlap heuristic only; "
            "not a semantic factuality assessment."
        )
    }
