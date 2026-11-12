import html
import streamlit as st

from frontend.api_client import APIClient
from frontend.sidebar import render_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Human Review | Clinical Evidence AI",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# PROFESSIONAL DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: #f5f7fb;
}
.block-container {
    padding-top: 1.8rem;
    max-width: 1450px;
}
[data-testid="stSidebarNav"] {
    display: none !important;
}
.page-header {
    background: linear-gradient(120deg, #132b4e, #1b5270);
    padding: 27px 30px;
    border-radius: 15px;
    margin-bottom: 25px;
}
.page-header h1 {
    color: white !important;
    font-size: 27px !important;
    margin-bottom: 7px;
}
.page-header p {
    color: #d5e5f3;
    font-size: 13px;
    margin: 0;
}
.review-card {
    background: white;
    border: 1px solid #e5eaf2;
    border-radius: 13px;
    padding: 20px;
    margin-bottom: 15px;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5eaf2;
    padding: 16px;
    border-radius: 12px;
}
.stButton button,
.stFormSubmitButton button {
    border-radius: 9px;
    font-weight: 600;
    min-height: 42px;
}
[data-testid="stAlert"] {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access Human Review.")
    st.stop()

token = st.session_state.get("token")

if not token:
    st.error("Authentication token is missing. Please log in again.")
    st.stop()


# --------------------------------------------------
# COMMON SIDEBAR - RESTORED
# --------------------------------------------------

user = st.session_state.get("user", {})
render_sidebar(user)


# --------------------------------------------------
# API CLIENT
# --------------------------------------------------

client = APIClient(token)


def unwrap_response(response):
    if not isinstance(response, dict):
        raise ValueError("Unexpected API response.")
    return response.get("data", response)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown("""
<div class="page-header">
    <h1>Human Review Workspace</h1>
    <p>
        Review AI-generated clinical evidence reports,
        inspect validation results and record reviewer decisions.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD SAVED WORKFLOWS
# --------------------------------------------------

st.subheader("Select Workflow")

st.caption(
    "Select a previously saved workflow. Its report and "
    "validation details will load automatically."
)

try:
    with st.spinner("Loading saved workflows..."):
        response = client.get("/workflows/")

    workflow_list = unwrap_response(response)

    if not isinstance(workflow_list, list):
        raise ValueError("Invalid workflow list response.")

except Exception as exc:
    st.error(f"Unable to load saved workflows: {exc}")
    st.stop()


workflow_options = {}

for item in workflow_list:

    if not isinstance(item, dict):
        continue

    workflow_id = item.get("workflow_id")

    if not workflow_id:
        continue

    case_id = item.get("case_id", "Unknown Case")
    status = str(
        item.get("status", "unknown")
    ).replace("_", " ").title()

    workflow_options[workflow_id] = (
        f"{workflow_id} | Case: {case_id} | Status: {status}"
    )


if not workflow_options:
    st.info(
        "No saved workflows found. Please execute an AI workflow first."
    )
    st.stop()


# --------------------------------------------------
# WORKFLOW DROPDOWN
# --------------------------------------------------

saved_workflow_ids = list(workflow_options.keys())

previous_workflow = st.session_state.get("workflow_result", {})

preferred_workflow_id = None

if isinstance(previous_workflow, dict):
    preferred_workflow_id = previous_workflow.get("workflow_id")

if (
    preferred_workflow_id
    and preferred_workflow_id in saved_workflow_ids
):
    default_index = saved_workflow_ids.index(preferred_workflow_id)
else:
    default_index = 0


selected_workflow_id = st.selectbox(
    "Saved Workflow ID",
    options=saved_workflow_ids,
    index=default_index,
    format_func=lambda value: workflow_options.get(value, value),
    key="human_review_workflow_selector"
)


# --------------------------------------------------
# LOAD SELECTED WORKFLOW DETAILS
# --------------------------------------------------

try:
    with st.spinner("Loading selected workflow details..."):
        detail_response = client.get(
            f"/workflows/{selected_workflow_id}"
        )

    workflow_record = unwrap_response(detail_response)

    if not isinstance(workflow_record, dict):
        raise ValueError("Invalid workflow details response.")

    workflow_result = workflow_record.get("result", {})

    if not isinstance(workflow_result, dict):
        workflow_result = {}

    workflow_result = {
        **workflow_result,
        "workflow_id": workflow_record.get(
            "workflow_id", selected_workflow_id
        ),
        "case_id": workflow_record.get("case_id"),
        "status": workflow_record.get(
            "status",
            workflow_result.get("status", "unknown")
        ),
        "current_node": workflow_record.get(
            "current_node",
            workflow_result.get("current_node")
        )
    }

    # Store selected workflow separately from review response.
    st.session_state.workflow_result = workflow_result

except Exception as exc:
    st.error(f"Unable to load selected workflow: {exc}")
    st.stop()


# --------------------------------------------------
# WORKFLOW DATA
# --------------------------------------------------

report = workflow_result.get("report", {})
validation = workflow_result.get("validation", {})
safety = workflow_result.get("safety", {})

if not isinstance(report, dict):
    report = {}

if not isinstance(validation, dict):
    validation = {}

if not isinstance(safety, dict):
    safety = {}


# --------------------------------------------------
# WORKFLOW OVERVIEW
# --------------------------------------------------

st.divider()
st.subheader("Workflow Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Workflow Status",
    str(workflow_result.get("status", "Unknown"))
    .replace("_", " ").title()
)

col2.metric(
    "Validation",
    "Passed" if validation.get("is_valid") is True
    else "Failed" if validation.get("is_valid") is False
    else "Unavailable"
)

col3.metric(
    "Safety Level",
    str(safety.get("safety_level", "Unknown")).title()
)

safe_workflow_id = html.escape(str(selected_workflow_id))

st.markdown(
    f"""
    <div class="review-card">
        <p style="color:#64748b;font-size:12px;">
            SELECTED WORKFLOW ID
        </p>
        <p style="color:#172b4d;font-weight:600;
                  font-size:13px;word-break:break-all;">
            {safe_workflow_id}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# CLINICAL EVIDENCE REPORT
# --------------------------------------------------

st.divider()
st.subheader("Clinical Evidence Report")

st.markdown(
    f"### {report.get('title', 'Clinical Evidence Report')}"
)

st.caption(report.get("clinical_question", ""))

st.markdown(
    '<div class="review-card">',
    unsafe_allow_html=True
)

st.markdown("**Executive Summary**")

st.write(report.get("executive_summary", "Not available."))

st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
# RESEARCH FINDINGS
# --------------------------------------------------

findings = report.get("findings", [])

if findings:

    st.markdown("#### Research Findings")

    for index, finding in enumerate(findings, 1):

        if not isinstance(finding, dict):
            continue

        with st.expander(
            f"{index}. {finding.get('heading', 'Finding')}",
            expanded=True
        ):

            st.write(finding.get("content", ""))

            citation_ids = finding.get("citation_ids", [])

            if isinstance(citation_ids, list):
                st.caption(
                    "Citation references: "
                    + ", ".join(str(item) for item in citation_ids)
                )


# --------------------------------------------------
# EVIDENCE LIMITATIONS
# --------------------------------------------------

st.markdown("#### Evidence Limitations")

limitations = report.get("evidence_limitations", [])

if limitations:
    for item in limitations:
        st.write(f"• {item}")
else:
    st.info("No evidence limitations supplied in this report.")


# --------------------------------------------------
# SUPPORTING CITATIONS
# --------------------------------------------------

citations = report.get("citations", [])

st.markdown("#### Supporting Citations")

if citations:

    for citation in citations:

        if not isinstance(citation, dict):
            continue

        with st.expander(
            str(citation.get("citation_id", "Citation"))
        ):

            st.write(
                "**Source:**",
                citation.get("source", "Not available")
            )

            st.write(
                "**Page:**",
                citation.get("page", "Not available")
            )

            st.write(
                "**Chunk ID:**",
                citation.get("chunk_id", "Not available")
            )

else:
    st.info("No citations are available in the workflow response.")


# --------------------------------------------------
# VALIDATION ASSESSMENT
# --------------------------------------------------

st.divider()
st.subheader("Validation Assessment")

validation_fields = [
    ("Schema Validation", "schema_valid"),
    ("Citation Validation", "citation_valid"),
    ("Groundedness Validation", "groundedness_valid"),
    ("Safety Validation", "safety_valid")
]

validation_columns = st.columns(2)

for index, (label, key) in enumerate(validation_fields):

    value = validation.get(key)

    with validation_columns[index % 2]:

        if value is True:
            st.success(f"✓ {label}: Passed")
        elif value is False:
            st.error(f"✗ {label}: Failed")
        else:
            st.warning(f"— {label}: Unavailable")


if validation.get("is_valid") is True:
    st.success("Overall validation passed.")
elif validation.get("is_valid") is False:
    st.error("Overall validation failed.")
else:
    st.info("Overall validation result is unavailable.")


issues = validation.get("issues", [])

if issues:

    with st.expander("View Validation Issues"):

        for issue in issues:

            if isinstance(issue, dict):
                st.write(
                    f"**{issue.get('category', 'Issue')}**: "
                    f"{issue.get('message', '')}"
                )
            else:
                st.write(issue)


# --------------------------------------------------
# SAFETY ASSESSMENT
# --------------------------------------------------

st.divider()
st.subheader("Safety Policy Assessment")

safety_level = safety.get("safety_level", "unknown")

if safety_level == "safe":
    st.success("Safety level: Safe")
elif safety_level == "warning":
    st.warning("Safety level: Warning")
else:
    st.error(f"Safety level: {str(safety_level).title()}")


for finding in safety.get("findings", []):

    if isinstance(finding, dict):
        st.write(finding.get("message", ""))

if safety.get("disclaimer"):
    st.caption(safety.get("disclaimer"))


# --------------------------------------------------
# REVIEW DECISION
# --------------------------------------------------

st.divider()
st.subheader("Submit Review Decision")

st.caption(
    "Inspect the report and validation results before submitting "
    "your decision."
)

approval_checks_passed = all([
    validation.get("is_valid") is True,
    validation.get("schema_valid") is True,
    validation.get("citation_valid") is True,
    validation.get("groundedness_valid") is True,
    validation.get("safety_valid") is True,
    safety.get("is_safe") is True,
    safety.get("safety_level") != "blocked"
])

if approval_checks_passed:
    st.success("All available approval checks passed.")
else:
    st.warning(
        "Approval is unavailable based on the current workflow "
        "validation and safety information. Rejection or revision "
        "may still be submitted."
    )


# --------------------------------------------------
# REVIEW SUBMISSION FORM
# --------------------------------------------------

decision_options = [
    "rejected",
    "revision_required"
]

if approval_checks_passed:
    decision_options.insert(0, "approved")


with st.form("human_review_form"):

    decision = st.selectbox(
        "Review Decision",
        options=decision_options,
        format_func=lambda value: {
            "approved": "✓ Approve Report",
            "rejected": "✕ Reject Report",
            "revision_required": "↻ Request Revision"
        }.get(value, value)
    )

    comments = st.text_area(
        "Reviewer Comments",
        placeholder=(
            "Enter your review observations, reason for rejection "
            "or requested revisions..."
        ),
        height=140
    )

    submitted = st.form_submit_button(
        "Submit Review Decision",
        use_container_width=True,
        type="primary"
    )


if submitted:

    if decision == "revision_required" and not comments.strip():
        st.error("Please provide revision instructions.")

    else:

        try:

            with st.spinner("Submitting reviewer decision..."):

                response = client.post(
                    f"/reviews/{selected_workflow_id}/decision",
                    {
                        "decision": decision,
                        "comments": comments
                    }
                )

            review_data = unwrap_response(response)

            if not isinstance(review_data, dict):
                raise ValueError("Unexpected review API response.")

            # Do not overwrite workflow_result with review response.
            st.session_state.last_review_result = review_data

            if decision == "approved":
                st.success("Report approved successfully.")
            elif decision == "rejected":
                st.success("Report rejection recorded.")
            else:
                st.success("Revision request submitted successfully.")

            st.json(review_data)

        except Exception as exc:
            st.error(f"Unable to submit review: {exc}")


# --------------------------------------------------
# PREVIOUS REVIEW RESULT
# --------------------------------------------------

previous_review = st.session_state.get("last_review_result")

if previous_review:

    st.divider()
    st.subheader("Latest Review Response")

    if isinstance(previous_review, dict):

        st.write(
            "Status:",
            previous_review.get("status", "Not available")
        )

        st.write(
            "Decision:",
            previous_review.get(
                "review_decision",
                previous_review.get("decision", "Not available")
            )
        )

        with st.expander("View complete response"):
            st.json(previous_review)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown("""
<div style="text-align:center;color:#94a3b8;
            font-size:12px;padding:15px;">
    Clinical Evidence AI · Human Review Workspace
</div>
""", unsafe_allow_html=True)