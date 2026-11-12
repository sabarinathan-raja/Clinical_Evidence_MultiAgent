
from evaluation.retrieval_metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    evaluate_retrieval
)

from evaluation.groundedness import (
    evaluate_groundedness
)

from evaluation.citation_evaluation import (
    evaluate_citations
)

from evaluation.answer_quality import (
    evaluate_answer_quality
)

from evaluation.safety_evaluation import (
    evaluate_safety
)


def test_precision():

    score = precision_at_k(
        ["A", "B", "C"],
        ["A", "C"],
        3
    )

    assert round(score, 2) == 0.67


def test_recall():

    score = recall_at_k(
        ["A", "B"],
        ["A", "B", "C"],
        2
    )

    assert round(score, 2) == 0.67


def test_reciprocal_rank():

    score = reciprocal_rank(
        ["A", "B", "C"],
        ["B"]
    )

    assert score == 0.5


def test_retrieval_metrics():

    result = evaluate_retrieval(
        ["A", "B"],
        ["A"],
        k=2
    )

    assert result["precision_at_k"] == 0.5
    assert result["recall_at_k"] == 1.0


def test_groundedness():

    result = evaluate_groundedness(
        "Clinical research evidence shows outcomes",
        "Clinical research evidence shows outcomes"
    )

    assert result["score"] == 1.0
    assert result["grounded"] is True


def test_citation_evaluation():

    result = evaluate_citations(
        {
            "findings": [
                {
                    "citation_ids": ["E1"]
                }
            ]
        },
        [{"citation_id": "E1"}]
    )

    assert result["is_valid"] is True
    assert result["citation_accuracy"] == 1.0


def test_answer_quality():

    result = evaluate_answer_quality(
        {
            "executive_summary": "Evidence summary",
            "findings": [
                {"citation_ids": ["E1"]}
            ],
            "evidence_limitations": ["Synthetic limitation"]
        }
    )

    assert result["structural_score"] == 1.0


def test_safety_evaluation():

    result = evaluate_safety(
        report={
            "review_status": "pending"
        },
        safety_result={
            "safety_level": "safe"
        },
        validation_result={
            "is_valid": True
        }
    )

    assert result["is_safe"] is True
