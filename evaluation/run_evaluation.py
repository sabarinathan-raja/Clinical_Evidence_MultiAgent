
import json
import argparse
from pathlib import Path

from evaluation.retrieval_metrics import evaluate_retrieval
from evaluation.groundedness import evaluate_groundedness
from evaluation.citation_evaluation import evaluate_citations
from evaluation.answer_quality import evaluate_answer_quality
from evaluation.safety_evaluation import evaluate_safety


def run_evaluation(
    dataset_path,
    report_path=None
):

    path = Path(dataset_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    dataset = json.loads(
        path.read_text(encoding="utf-8")
    )

    results = []

    for item in dataset:

        results.append({
            "id": item["id"],
            "synthetic": item.get("synthetic", False),
            "status": "dataset_loaded",
            "query": item["query"],
            "retrieval_ground_truth": (
                item.get("relevant_document_ids", [])
            )
        })

    output = {
        "total_samples": len(results),
        "dataset_type": "synthetic",
        "results": results,
        "metrics": {
            "retrieval": (
                "Requires actual retrieved document IDs."
            ),
            "groundedness": (
                "Requires generated answers and evidence context."
            ),
            "citations": (
                "Requires generated reports and citation records."
            ),
            "answer_quality": (
                "Requires generated reports."
            ),
            "safety": (
                "Requires safety and validation outputs."
            )
        },
        "note": (
            "Dataset loading is not equivalent to a completed "
            "model evaluation. Connect actual workflow outputs "
            "to calculate these metrics."
        )
    }

    if report_path:
        destination = Path(report_path)
        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        destination.write_text(
            json.dumps(output, indent=2),
            encoding="utf-8"
        )

    return output


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        default="evaluation/datasets/sample_evaluation.json"
    )

    parser.add_argument(
        "--output",
        default="evaluation/results.json"
    )

    args = parser.parse_args()

    result = run_evaluation(
        args.dataset,
        args.output
    )

    print(json.dumps(result, indent=2))
