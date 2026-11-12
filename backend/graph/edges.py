
from langgraph.graph import END


def route_after_safety(state):

    if state.get("safety_blocked"):
        return "safety_block"

    return "summary_generation"


def route_after_validation(state):

    # Both valid and invalid reports enter human review.
    # Invalid reports cannot be approved.
    return "human_review"


def route_after_review(state):

    decision = state.get("review_decision")

    if decision == "approved":
        return END

    if decision == "rejected":
        return END

    if decision == "revision_required":
        return END

    return END
