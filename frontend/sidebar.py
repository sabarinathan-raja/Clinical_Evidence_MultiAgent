
import streamlit as st

from frontend.auth import logout


def render_sidebar(user=None):

    user = user or {}

    full_name = str(user.get("full_name", "Researcher"))
    role = str(user.get("role", "Researcher")).upper()

    # ---------------------------------------------
    # SIDEBAR CSS
    # ---------------------------------------------

    st.markdown("""
    <style>

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #101d35 0%,
            #173c68 100%
        ) !important;

        min-width: 260px;
        border-right: 1px solid #253550;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #c2cee0;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }

    [data-testid="stSidebar"] .stButton button {
        background: #1c2d49;
        border: 1px solid #344965;
        color: white;
        border-radius: 9px;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: #294366;
        border-color: #5b84b5;
    }

    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    [data-testid="stSidebar"] a[aria-current="page"] {
        background: #294366;
        border-radius: 8px;
        font-weight: 700;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------
    # SIDEBAR CONTENT
    # ---------------------------------------------

    with st.sidebar:

        # Branding - native Streamlit components
        st.markdown("## 🧬")

        st.title("Clinical Evidence AI")

        st.caption("MULTI-AGENT RESEARCH PLATFORM")

        st.divider()

        st.caption("WORKSPACE")

        # Navigation
        st.page_link(
            "app.py",
            label="Dashboard",
            icon="🏠"
        )

        st.page_link(
            "pages/1_Clinical_Cases.py",
            label="Clinical Cases",
            icon="📁"
        )

        st.page_link(
            "pages/2_Document_Upload.py",
            label="Document Upload",
            icon="📄"
        )

        st.page_link(
            "pages/3_AI_Workflow.py",
            label="AI Workflow",
            icon="🤖"
        )

        st.page_link(
            "pages/4_Human_Review.py",
            label="Human Review",
            icon="✅"
        )

        st.page_link(
            "pages/5_Reports.py",
            label="Reports",
            icon="📊"
        )

        st.divider()

        st.caption("ACCOUNT")

        # User information
        st.markdown(f"**{full_name}**")

        st.caption(role)

        if st.button(
            "Logout",
            use_container_width=True
        ):
            logout()
