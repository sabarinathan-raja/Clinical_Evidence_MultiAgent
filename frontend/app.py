
import sys
from pathlib import Path

import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.auth import login_page
from frontend.api_client import APIClient
from frontend.sidebar import render_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Clinical Evidence AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Hide sidebar navigation before login
if not st.session_state.get("authenticated", False):
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

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
    padding-bottom: 2rem;
    max-width: 1500px;
}

h1, h2, h3 {
    color: #172b4d;
    font-weight: 700;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5eaf2;
    padding: 20px;
    border-radius: 13px;
    box-shadow: 0 3px 12px rgba(25,45,75,0.04);
}

[data-testid="stMetricLabel"] {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #172b4d;
    font-weight: 700;
}

.stButton button {
    border-radius: 9px;
    font-weight: 600;
    min-height: 40px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #e5eaf2;
    border-radius: 10px;
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
    login_page()
    st.stop()

if not st.session_state.get("token"):
    st.error("Authentication token is missing. Please log in again.")
    st.stop()


# --------------------------------------------------
# API CLIENT
# --------------------------------------------------

client = APIClient(st.session_state.token)

user = st.session_state.get("user", {})


# --------------------------------------------------
# COMMON SIDEBAR
# --------------------------------------------------

render_sidebar(user)


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("🧬 Clinical Research Dashboard")

st.caption(
    "Intelligent evidence retrieval, multi-agent clinical "
    "research and human-reviewed reporting."
)

st.divider()


# --------------------------------------------------
# DASHBOARD DATA
# --------------------------------------------------

try:

    result = client.get("/cases/")

    if not isinstance(result, dict):
        raise ValueError("Unexpected backend response.")

    cases = result.get("data", [])

    if not isinstance(cases, list):
        cases = []

    # ----------------------------------------------
    # CASE STATUS COUNTS
    # ----------------------------------------------

    total = len(cases)

    pending = sum(
        1 for case in cases
        if case.get("status") == "review_pending"
    )

    approved = sum(
        1 for case in cases
        if case.get("status") == "approved"
    )

    rejected = sum(
        1 for case in cases
        if case.get("status") == "rejected"
    )

    # ----------------------------------------------
    # WORKSPACE OVERVIEW
    # ----------------------------------------------

    st.subheader("Workspace Overview")

    st.caption(
        "Overview of your clinical evidence research activities."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cases", total)
    col2.metric("Pending Review", pending)
    col3.metric("Approved Cases", approved)
    col4.metric("Rejected Cases", rejected)

    st.divider()

    # ----------------------------------------------
    # RECENT CLINICAL CASES
    # ----------------------------------------------

    left, right = st.columns([3, 1])

    with left:
        st.subheader("Recent Clinical Cases")
        st.caption("Monitor and access your research cases.")

    with right:
        if st.button(
            "↻ Refresh Dashboard",
            use_container_width=True
        ):
            st.rerun()

    if cases:

        df = pd.DataFrame(cases)

        preferred_columns = [
            "id",
            "title",
            "status",
            "created_at"
        ]

        available_columns = [
            column
            for column in preferred_columns
            if column in df.columns
        ]

        display_df = (
            df[available_columns]
            if available_columns
            else df
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No clinical cases available. "
            "Create your first clinical case to get started."
        )

    # ----------------------------------------------
    # QUICK ACCESS
    # ----------------------------------------------

    st.divider()

    st.subheader("Quick Access")

    st.caption(
        "Navigate directly to important research activities."
    )

    q1, q2, q3 = st.columns(3)

    with q1:

        with st.container(border=True):

            st.subheader("📁 Clinical Cases")

            st.caption(
                "Create and manage clinical research cases."
            )

            st.page_link(
                "pages/1_Clinical_Cases.py",
                label="Open Clinical Cases",
                icon="arrow-right"
            )

    with q2:

        with st.container(border=True):

            st.subheader("🤖 AI Workflow")

            st.caption(
                "Execute the multi-agent research pipeline."
            )

            st.page_link(
                "pages/3_AI_Workflow.py",
                label="Open AI Workflow",
                icon="arrow-right"
            )

    with q3:

        with st.container(border=True):

            st.subheader("📊 Research Reports")

            st.caption(
                "Access generated clinical evidence reports."
            )

            st.page_link(
                "pages/5_Reports.py",
                label="View Reports",
                icon="arrow-right"
            )


except Exception as exc:

    st.error(f"Backend connection failed: {exc}")

    st.info(
        "Check whether your FastAPI backend is running "
        "and API configuration is correct."
    )


# --------------------------------------------------
# CLINICAL RESEARCH DISCLAIMER
# --------------------------------------------------

st.divider()

with st.container(border=True):

    st.subheader("Clinical Research Disclaimer")

    st.write(
        "This platform supports clinical evidence research "
        "and summarization. It does not provide diagnosis, "
        "prescribe treatment or replace qualified clinical "
        "judgment. Generated reports require appropriate "
        "human review."
    )

st.caption(
    "Clinical Evidence AI · Multi-Agent Research Platform"
)
