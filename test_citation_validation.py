
from backend.agents.output_validation_agent import (
    output_validation_agent
)

allowed = [
    {
        "citation_id": "E1",
        "chunk_id": "chunk-001",
        "source": "nice.pdf",
        "page": 72
    }
]

report = {
    "executive_summary": "Evidence summary.",
    "findings": [
        {
            "heading": "DKA risk",
            "content": "Risk should be assessed.",
            "citation_ids": ["E1"]
        }
    ],
    "evidence_limitations": [],
    "citations": [
        {
            "citation_id": "E1",
            "chunk_id": "chunk-001",
            "source": "nice.pdf",
            "page": 72
        }
    ]
}

result = output_validation_agent.run(report, allowed)

print("VALID CITATION TEST")
print(result)

assert result["citation_valid"] is True

# Test an incorrect page number
wrong_report = {
    **report,
    "citations": [
        {
            "citation_id": "E1",
            "chunk_id": "chunk-001",
            "source": "nice.pdf",
            "page": 99
        }
    ]
}

wrong_result = output_validation_agent.run(
    wrong_report,
    allowed
)

print("\nINVALID PAGE TEST")
print(wrong_result)

assert wrong_result["citation_valid"] is False

print("\nALL CITATION TESTS PASSED")
