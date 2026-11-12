import html
import streamlit as st

from frontend.api_client import APIClient
from frontend.sidebar import render_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Workflow | Clinical Evidence AI",
    page_icon="🤖",
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
.workflow-card {
    background: white;
    border: 1px solid #e5eaf2;
    border-radius: 13px;
    padding: 20px;
    margin-bottom: 15px;
}
.agent-card {
    background: white;
    border: 1px solid #e5eaf2;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 9px;
}
.agent-name {
    color: #172b4d;
    font-size: 14px;
    font-weight: 650;
}
.agent-description {
    color: #74839a;
    font-size: 12px;
    margin-top: 5px;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5eaf2;
    padding: 17px;
    border-radius: 12px;
}
.stButton button {
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
    st.warning("Please log in to access AI Workflow.")
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
    <h1>AI Multi-Agent Workflow</h1>
    <p>
        Execute intelligent evidence retrieval, clinical
        evidence assessment, safety checks and report generation.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# AGENT INFORMATION
# --------------------------------------------------

AGENT_DETAILS = {
    "intake_scope_agent": {
        "name": "Intake & Scope Agent",
        "description": "Understands the clinical question and defines research scope."
    },
    "patient_context_agent": {
        "name": "Patient Context Agent",
        "description": "Processes and de-identifies available patient context."
    },
    "evidence_retrieval_agent": {
        "name": "Evidence Retrieval Agent",
        "description": "Retrieves relevant evidence from indexed documents."
    },
    "evidence_quality_agent": {
        "name": "Evidence Quality Agent",
        "description": "Assesses evidence metadata and retrieval relevance."
    },
    "safety_policy_agent": {
        "name": "Safety Policy Agent",
        "description": "Checks potentially unsafe requests and urgent context."
    },
    "summary_generation_agent": {
        "name": "Summary Generation Agent",
        "description": "Generates an evidence-grounded research summary."
    },
    "output_validation_agent": {
        "name": "Output Validation Agent",
        "description": "Validates report structure, citations and groundedness."
    },
    "safety_block_node": {
        "name": "Safety Block",
        "description": "Stops automated summary generation for blocked requests."
    }
}


# --------------------------------------------------
# CASE SELECTION
# --------------------------------------------------

st.subheader("Select Research Case")
st.caption("Choose the clinical case for multi-agent execution.")

case_id = st.text_input(
    "Clinical Case ID",
    value=str(st.session_state.get("selected_case") or ""),
    placeholder="Enter or select a Clinical Case ID"
)

if case_id.strip():
    st.session_state.selected_case = case_id.strip()


# --------------------------------------------------
# WORKFLOW EXECUTION
# --------------------------------------------------

with st.container(border=True):
    st.subheader("Workflow Execution")
    st.caption(
        "Start the multi-agent pipeline for the selected research case."
    )

run_col, info_col = st.columns([1, 2])

with run_col:
    run_clicked = st.button(
        "▶ Run Multi-Agent Workflow",
        use_container_width=True,
        type="primary"
    )

with info_col:
    st.caption(
        "Execution includes evidence retrieval, quality assessment, "
        "safety policy, summary generation and output validation."
    )


if run_clicked:
    if not case_id.strip():
        st.warning("Please select a clinical case.")
    else:
        try:
            with st.spinner(
                "Executing agents and retrieving clinical evidence..."
            ):
                response = client.post(
                    f"/workflows/{case_id.strip()}/run"
                )

            workflow_data = unwrap_response(response)

            if not isinstance(workflow_data, dict):
                raise ValueError("Invalid workflow result format.")

            workflow_id = workflow_data.get("workflow_id")

            if not workflow_id:
                raise ValueError(
                    "Workflow ID was not returned by the backend. "
                    "Check the backend workflow route."
                )

            st.session_state.workflow_result = workflow_data
            st.success("Workflow execution completed successfully.")
            st.code(workflow_id)

            st.rerun()

        except Exception as exc:
            st.error(f"Workflow execution failed: {exc}")


# --------------------------------------------------
# WORKFLOW RESULT
# --------------------------------------------------

result = st.session_state.get("workflow_result")

if isinstance(result, dict) and result:

    st.divider()
    st.subheader("Workflow Execution Overview")

    status = result.get("status", "unknown")
    workflow_id = result.get("workflow_id", "Not available")
    current_node = result.get("current_node", "Not available")

    completed_agents = result.get("completed_agents", [])
    if not isinstance(completed_agents, list):
        completed_agents = []

    validation = result.get("validation", {})
    if not isinstance(validation, dict):
        validation = {}

    total_agents = 7

    completed_count = sum(
        1 for agent in completed_agents
        if agent in AGENT_DETAILS and agent != "safety_block_node"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Workflow Status",
        str(status).replace("_", " ").title()
    )
    col2.metric(
        "Completed Agents",
        f"{completed_count}/{total_agents}"
    )
    col3.metric(
        "Current Node",
        str(current_node).replace("_", " ").title()
    )

    safe_workflow_id = html.escape(str(workflow_id))

    st.markdown(
        f"""
        <div class="workflow-card">
            <p style="color:#64748b;font-size:12px;">
                WORKFLOW IDENTIFIER
            </p>
            <p style="color:#172b4d;font-weight:600;
                      font-size:13px;word-break:break-all;">
                {safe_workflow_id}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Agent progress
    st.subheader("Agent Execution Pipeline")

    st.progress(
        min(completed_count / total_agents, 1.0),
        text=f"{completed_count} of {total_agents} agents completed"
    )

    for agent_key, details in AGENT_DETAILS.items():

        completed = agent_key in completed_agents

        if completed:
            icon = "✅"
            agent_status = "Completed"
        elif agent_key == current_node:
            icon = "🔄"
            agent_status = "Current"
        else:
            icon = "⏳"
            agent_status = "Not completed"

        st.markdown(
            f"""
            <div class="agent-card">
                <div style="display:flex;justify-content:space-between;
                            gap:10px;flex-wrap:wrap;">
                    <span class="agent-name">
                        {icon} {details["name"]}
                    </span>
                    <span style="font-size:11px;color:#64748b;">
                        {agent_status}
                    </span>
                </div>
                <div class="agent-description">
                    {details["description"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Validation
    st.divider()
    st.subheader("Output Validation")

    if validation:

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
                    st.warning(f"— {label}: Not available")

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
    else:
        st.info("Validation results are not available.")

    # Safety
    safety = result.get("safety", {})

    if isinstance(safety, dict) and safety:

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

        st.caption(safety.get("disclaimer", ""))

    # Human review navigation
    st.divider()
    st.subheader("Human Review")

    if result.get("review_required", False):
        st.warning(
            "Human review is required before this report can be finalized."
        )
        st.write(
            "Open the Human Review page to inspect the report "
            "and submit an authorized review decision."
        )
        st.page_link(
            "pages/4_Human_Review.py",
            label="Open Human Review",
            icon=":material/check_circle:"
        )
    else:
        decision = result.get("review_decision")

        if decision == "approved":
            st.success("Report approved by human reviewer.")
        elif decision == "rejected":
            st.error("Report rejected by human reviewer.")
        elif decision == "revision_required":
            st.warning("Report requires revision.")
        else:
            st.info("Human review status is not available.")

    # Report preview
    report = result.get("report", {})

    if isinstance(report, dict) and report:

        st.divider()
        st.subheader("Generated Report Preview")

        st.markdown(
            f"### {report.get('title', 'Clinical Evidence Report')}"
        )

        st.write(report.get("executive_summary", ""))

        findings = report.get("findings", [])

        if findings:
            st.markdown("#### Key Findings")

            for index, finding in enumerate(findings, 1):

                if not isinstance(finding, dict):
                    continue

                with st.expander(
                    f"{index}. {finding.get('heading', 'Finding')}"
                ):
                    st.write(finding.get("content", ""))

                    citation_ids = finding.get("citation_ids", [])

                    if isinstance(citation_ids, list):
                        st.caption(
                            "Citations: "
                            + ", ".join(str(item) for item in citation_ids)
                        )

        with st.expander("View Complete Workflow Result"):
            st.json(result)


# --------------------------------------------------
# SAVED WORKFLOWS
# --------------------------------------------------

st.divider()
st.subheader("Saved Workflows")

st.caption(
    "Workflows saved in the database. Select an ID from the "
    "Human Review page to load its details."
)

refresh_col, info_col = st.columns([1, 3])

with refresh_col:
    refresh_workflows = st.button(
        "🔄 Refresh Workflows",
        use_container_width=True
    )

with info_col:
    st.caption("This list is retrieved directly from the backend database.")

if refresh_workflows:
    st.rerun()

try:
    with st.spinner("Loading saved workflows..."):
        saved_response = client.get("/workflows/")

    saved_workflows = unwrap_response(saved_response)

    if not isinstance(saved_workflows, list):
        raise ValueError("Invalid saved workflows response.")

    table_rows = []

    for workflow in saved_workflows:
        if not isinstance(workflow, dict):
            continue

        table_rows.append({
            "Workflow ID": workflow.get("workflow_id", ""),
            "Case ID": workflow.get("case_id", ""),
            "Status": str(
                workflow.get("status", "unknown")
            ).replace("_", " ").title(),
            "Current Node": str(
                workflow.get("current_node") or "Not available"
            ).replace("_", " ").title(),
            "Started At": workflow.get("started_at") or "Not available"
        })

    if table_rows:
        st.dataframe(
            table_rows,
            use_container_width=True,
            hide_index=True
        )
        st.success(f"{len(table_rows)} saved workflow(s) found.")
    else:
        st.info(
            "No saved workflows found. Run an AI workflow to create one."
        )

except Exception as exc:
    st.error(f"Unable to load saved workflows: {exc}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Clinical Evidence AI · Multi-Agent Workflow Engine")