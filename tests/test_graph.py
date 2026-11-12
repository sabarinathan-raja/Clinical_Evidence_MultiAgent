
from backend.graph.edges import (
    route_after_safety,
    route_after_validation,
    route_after_review
)

from backend.graph.orchestrator import (
    ClinicalEvidenceOrchestrator
)


def test_safety_routing():

    blocked = {
        "safety_blocked": True
    }

    safe = {
        "safety_blocked": False
    }

    assert route_after_safety(blocked) == "safety_block"
    assert route_after_safety(safe) == "summary_generation"


def test_validation_routing():

    result = route_after_validation({
        "validation_result": {
            "is_valid": True
        }
    })

    assert result == "human_review"


def test_review_routing():

    assert route_after_review({
        "review_decision": "approved"
    }) == "__end__"

    assert route_after_review({
        "review_decision": "rejected"
    }) == "__end__"


def test_graph_compilation():

    orchestrator = ClinicalEvidenceOrchestrator()

    graph = orchestrator.build_graph()

    assert graph is not None


def test_checkpoint_config():

    from backend.graph.checkpoints import checkpoint_manager

    config = checkpoint_manager.get_config(
        "synthetic-thread"
    )

    assert config["configurable"]["thread_id"] == "synthetic-thread"
