
import json
import html
import streamlit as st

from frontend.api_client import APIClient
from frontend.sidebar import render_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Clinical Evidence Reports | Clinical Evidence AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# PROFESSIONAL STYLING
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

.report-card {
    background: white;
    border: 1px solid #e5eaf2;
    border-radius: 13px;
    padding: 22px;
    margin-bottom: 16px;
}

.finding-card {
    background: white;
    border: 1px solid #e5eaf2;
    border-left: 4px solid #287d91;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 12px;
}

.citation-card {
    background: #f8fafc;
    border: 1px solid #e5eaf2;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 10px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5eaf2;
    padding: 16px;
    border-radius: 12px;
}

.stButton button,
.stDownloadButton button {
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
    st.warning("Please log in to access Clinical Evidence Reports.")
    st.stop()

if not st.session_state.get("token"):
    st.error("Authentication token is missing. Please log in again.")
    st.stop()


# --------------------------------------------------
# COMMON SIDEBAR
# --------------------------------------------------

user = st.session_state.get("user", {})
render_sidebar(user)


# --------------------------------------------------
# API CLIENT
# --------------------------------------------------

client = APIClient(st.session_state.token)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown("""
<div class="page-header">
    <h1>Clinical Evidence Reports</h1>
    <p>
        Access, inspect and review AI-generated
        clinical evidence research reports.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# REPORT LOADING
# --------------------------------------------------

st.subheader("Load Research Report")

st.caption(
    "Enter the workflow ID to retrieve its generated report."
)

workflow_result = st.session_state.get(
    "workflow_result", {}
)

default_workflow_id = (
    workflow_result.get("workflow_id", "")
    if isinstance(workflow_result, dict)
    else ""
)

col1, col2 = st.columns([3, 1])

with col1:

    workflow_id = st.text_input(
        "Workflow ID",
        value=default_workflow_id,
        placeholder="Enter workflow ID"
    )

with col2:

    st.write("")
    st.write("")

    load_clicked = st.button(
        "Load Report",
        use_container_width=True,
        type="primary"
    )


if load_clicked:

    if not workflow_id.strip():

        st.warning("Please enter a workflow ID.")

    else:

        try:

            with st.spinner(
                "Retrieving clinical evidence report..."
            ):

                result = client.get(
                    f"/reports/{workflow_id.strip()}"
                )

            if not isinstance(result, dict):
                raise ValueError("Unexpected report API response.")

            st.session_state.report = result
            st.session_state.report_workflow_id = workflow_id.strip()

            st.success("Report retrieved successfully.")

        except Exception as exc:

            st.error(f"Unable to load report: {exc}")

            st.session_state.report = None
            st.session_state.report_workflow_id = None


# --------------------------------------------------
# REPORT DISPLAY
# --------------------------------------------------

report_data = st.session_state.get("report")

if report_data and isinstance(report_data, dict):

    report = report_data.get("report", {})

    if not isinstance(report, dict):
        report = {}

    review_status = report_data.get(
        "review_status",
        report.get("review_status", "unknown")
    )

    findings = report.get("findings", [])
    citations = report.get("citations", [])
    limitations = report.get("evidence_limitations", [])

    if not isinstance(findings, list):
        findings = []

    if not isinstance(citations, list):
        citations = []

    if not isinstance(limitations, list):
        limitations = []

    # --------------------------------------------------
    # REPORT HEADER
    # --------------------------------------------------

    st.divider()

    safe_title = html.escape(
        str(report.get("title", "Research Report"))
    )

    safe_workflow_id = html.escape(
        str(st.session_state.get("report_workflow_id", workflow_id))
    )

    st.markdown(
        f"""
        <div class="report-card">
            <p style="font-size:11px;
                      color:#74839a;
                      font-weight:600;">
                CLINICAL EVIDENCE RESEARCH REPORT
            </p>
            <h2 style="color:#172b4d;
                       font-size:24px;">
                {safe_title}
            </h2>
            <p style="font-size:12px;color:#74839a;">
                Workflow ID: {safe_workflow_id}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # REPORT METRICS
    # --------------------------------------------------

    st.subheader("Report Overview")

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Review Status",
        str(review_status).replace("_", " ").title()
    )

    metric2.metric(
        "Research Findings",
        len(findings)
    )

    metric3.metric(
        "Citations",
        len(citations)
    )

    # --------------------------------------------------
    # CLINICAL QUESTION
    # --------------------------------------------------

    st.divider()

    st.subheader("Clinical Research Question")

    with st.container(border=True):

        st.write(
            report.get(
                "clinical_question",
                "Not available."
            )
        )

    # --------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------

    st.subheader("Executive Summary")

    with st.container(border=True):

        st.write(
            report.get(
                "executive_summary",
                "Executive summary is not available."
            )
        )

    # --------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------

    background = report.get("background", "")

    if background:

        st.subheader("Background")

        st.write(background)

    # --------------------------------------------------
    # FINDINGS
    # --------------------------------------------------

    st.divider()

    st.subheader("Research Findings")

    st.caption(
        "Evidence-grounded findings generated from retrieved documents."
    )

    if findings:

        for index, finding in enumerate(findings, 1):

            if not isinstance(finding, dict):
                continue

            heading = finding.get(
                "heading",
                "Research Finding"
            )

            content = finding.get("content", "")

            citation_ids = finding.get(
                "citation_ids",
                []
            )

            with st.expander(
                f"{index:02d} | {heading}",
                expanded=True
            ):

                st.write(content)

                if citation_ids:

                    st.caption(
                        "Supporting Citations: "
                        + ", ".join(
                            str(item)
                            for item in citation_ids
                        )
                    )

    else:

        st.info("No research findings are available.")

    # --------------------------------------------------
    # EVIDENCE LIMITATIONS
    # --------------------------------------------------

    st.divider()

    st.subheader("Evidence Limitations")

    if limitations:

        for index, limitation in enumerate(limitations, 1):

            st.warning(f"{index}. {limitation}")

    else:

        st.info("No evidence limitations were supplied.")

    # --------------------------------------------------
    # SAFETY NOTES
    # --------------------------------------------------

    safety_notes = report.get("safety_notes", [])

    if isinstance(safety_notes, list) and safety_notes:

        st.divider()

        st.subheader("Safety Notes")

        for note in safety_notes:
            st.info(note)

    # --------------------------------------------------
    # CITATIONS
    # --------------------------------------------------

    st.divider()

    st.subheader("Supporting Evidence & Citations")

    st.caption(
        "Source metadata associated with the generated report."
    )

    if citations:

        for citation in citations:

            if not isinstance(citation, dict):
                continue

            citation_id = str(
                citation.get("citation_id", "Citation")
            )

            with st.expander(citation_id):

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

                if citation.get("evidence_type"):

                    st.write(
                        "**Evidence Type:**",
                        citation["evidence_type"]
                    )

    else:

        st.warning("No citations are available in this report.")

    # --------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------

    conclusion = report.get("conclusion", "")

    if conclusion:

        st.divider()

        st.subheader("Conclusion")

        with st.container(border=True):
            st.write(conclusion)

    # --------------------------------------------------
    # REPORT EXPORT
    # --------------------------------------------------

    st.divider()

    st.subheader("Report Export")

    export_col1, export_col2 = st.columns(2)

    with export_col1:

        report_json = json.dumps(
            report_data,
            indent=4,
            ensure_ascii=False,
            default=str
        )

        st.download_button(
            "Download Report JSON",
            data=report_json,
            file_name="clinical_evidence_report.json",
            mime="application/json",
            use_container_width=True
        )

    with export_col2:

        if st.button(
            "Refresh Report",
            use_container_width=True
        ):
            st.rerun()


# --------------------------------------------------
# DISCLAIMER
# --------------------------------------------------

st.divider()

with st.container(border=True):

    st.markdown("**Clinical Research Disclaimer**")

    st.caption(
        "This report supports clinical evidence research and "
        "summarization. It does not provide diagnosis or prescribe "
        "treatment. Generated findings require appropriate human "
        "review and qualified clinical judgment."
    )

st.markdown(
    """
    <div style="text-align:center;
                color:#94a3b8;
                font-size:12px;
                padding:15px;">
        Clinical Evidence AI · Research Reporting Workspace
    </div>
    """,
    unsafe_allow_html=True
)
