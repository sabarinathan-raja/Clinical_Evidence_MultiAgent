
from backend.agents.intake_scope_agent import IntakeScopeAgent
from backend.agents.patient_context_agent import PatientContextAgent
from backend.agents.evidence_quality_agent import EvidenceQualityAgent
from backend.agents.safety_policy_agent import SafetyPolicyAgent
from backend.agents.output_validation_agent import OutputValidationAgent


def test_intake_agent(monkeypatch):

    agent = IntakeScopeAgent()

    monkeypatch.setattr(
        "backend.agents.intake_scope_agent.model_gateway.health_check",
        lambda: {"configured": False}
    )

    result = agent.run({
        "clinical_question": (
            "What evidence exists for clinical research?"
        )
    })

    assert result["is_valid"] is True
    assert result["normalized_question"]
    assert isinstance(
        result["extracted_keywords"], list
    )


def test_patient_context_agent():

    agent = PatientContextAgent()

    result = agent.run({
        "clinical_history": (
            "Contact patient@example.com"
        )
    })

    assert result["deidentified"] is True

    assert (
        "patient@example.com"
        not in result["patient_context"]["clinical_history"]
    )


def test_evidence_quality_agent():

    agent = EvidenceQualityAgent()

    result = agent.run([
        {
            "id": "E1",
            "title": "Synthetic research",
            "source": "test.pdf",
            "page": 1,
            "evidence_type": "systematic_review",
            "relevance_score": 0.9
        }
    ])

    assert len(result["assessments"]) == 1
    assert result["assessments"][0]["relevance"] == 0.9


def test_safety_agent():

    agent = SafetyPolicyAgent()

    result = agent.run(
        question="Please prescribe medication for this patient.",
        evidence=[]
    )

    assert result["safety_level"] == "blocked"
    assert result["is_safe"] is False


def test_output_validation_agent():

    agent = OutputValidationAgent()

    report = {
        "executive_summary": "Synthetic research summary",
        "findings": [
            {
                "heading": "Finding",
                "content": "Evidence-based observation",
                "citation_ids": ["E1"]
            }
        ],
        "evidence_limitations": [
            "Synthetic example"
        ]
    }

    result = agent.run(
        report,
        [{"citation_id": "E1"}]
    )

    assert result["is_valid"] is True
    assert result["citation_valid"] is True
