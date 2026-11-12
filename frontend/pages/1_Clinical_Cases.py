
import streamlit as st
from frontend.api_client import APIClient
from frontend.sidebar import render_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Clinical Cases | Clinical Evidence AI",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# SIMPLE PROFESSIONAL STYLING
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 1.5rem;
    max-width: 1400px;
}

[data-testid="stSidebarNav"] {
    display: none !important;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5eaf2;
    padding: 15px;
    border-radius: 10px;
}

.stButton button,
.stFormSubmitButton button {
    border-radius: 8px;
    font-weight: 600;
    min-height: 40px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

if not st.session_state.get("authenticated", False):
    st.warning("Please log in to access Clinical Cases.")
    st.stop()

token = st.session_state.get("token")

if not token:
    st.error("Authentication token is missing. Please log in again.")
    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

user = st.session_state.get("user", {})
render_sidebar(user)


# --------------------------------------------------
# API CLIENT
# --------------------------------------------------

client = APIClient(token)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📁 Clinical Case Management")

st.caption(
    "Create and manage clinical research cases in one workspace."
)

st.divider()


# --------------------------------------------------
# FETCH EXISTING CASES
# --------------------------------------------------

cases = []
load_error = None

try:
    result = client.get("/cases/")

    if not isinstance(result, dict):
        raise ValueError("Unexpected backend response.")

    cases = result.get("data", [])

    if not isinstance(cases, list):
        cases = []

except Exception as exc:
    load_error = str(exc)


# --------------------------------------------------
# CASE OVERVIEW
# --------------------------------------------------

st.subheader("Case Overview")

total_cases = len(cases)

pending_cases = sum(
    1 for case in cases
    if case.get("status") == "review_pending"
)

approved_cases = sum(
    1 for case in cases
    if case.get("status") == "approved"
)

rejected_cases = sum(
    1 for case in cases
    if case.get("status") == "rejected"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Cases", total_cases)
col2.metric("Pending Review", pending_cases)
col3.metric("Approved", approved_cases)
col4.metric("Rejected", rejected_cases)

st.divider()


# --------------------------------------------------
# CREATE NEW RESEARCH CASE
# --------------------------------------------------

st.subheader("➕ Create New Research Case")

st.caption(
    "Enter your clinical research question and patient context."
)

with st.container(border=True):

    with st.form("create_case_form", clear_on_submit=True):

        title = st.text_input(
            "Case Title",
            placeholder="Example: Type 2 Diabetes with Hypertension"
        )

        question = st.text_area(
            "Clinical Research Question",
            placeholder="Enter your clinical research question...",
            height=110
        )

        st.markdown("### Patient Context")

        col1, col2 = st.columns(2)

        with col1:

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=0,
                help="Enter 0 if age is not available."
            )

            gender = st.selectbox(
                "Gender",
                [
                    "Not specified",
                    "Male",
                    "Female",
                    "Other"
                ]
            )

            medical_history = st.text_area(
                "Medical History",
                placeholder="Example: Type 2 Diabetes (8 years)"
            )

            medications = st.text_area(
                "Current Medications",
                placeholder="Example: Metformin, Amlodipine"
            )

        with col2:

            blood_pressure = st.text_input(
                "Blood Pressure",
                placeholder="Example: 148/92 mmHg"
            )

            hba1c = st.text_input(
                "HbA1c",
                placeholder="Example: 8.2%"
            )

            egfr = st.text_input(
                "eGFR",
                placeholder="Example: 68 mL/min/1.73m²"
            )

            allergies = st.text_input(
                "Allergies",
                placeholder="Example: Not documented"
            )

        st.caption(
            "Use synthetic demo data. Avoid entering identifiable patient information."
        )

        submitted = st.form_submit_button(
            "Create Research Case",
            type="primary",
            use_container_width=True
        )

        if submitted:

            clean_title = title.strip()
            clean_question = question.strip()

            if not clean_title:

                st.error("Please enter a case title.")

            elif len(clean_question) < 10:

                st.error(
                    "Please enter a meaningful clinical research question."
                )

            else:

                patient_context = {
                    "age": age if age > 0 else None,
                    "gender": gender,
                    "medical_history": medical_history.strip(),
                    "blood_pressure": blood_pressure.strip(),
                    "hba1c": hba1c.strip(),
                    "egfr": egfr.strip(),
                    "current_medications": medications.strip(),
                    "allergies": allergies.strip()
                }

                payload = {
                    "title": clean_title,
                    "clinical_question": clean_question,
                    "patient_context": patient_context
                }

                try:

                    response = client.post(
                        "/cases/",
                        payload
                    )

                    if not isinstance(response, dict):
                        raise ValueError("Unexpected create-case response.")

                    created_data = response.get("data", {})

                    st.success(
                        "Clinical research case created successfully!"
                    )

                    if isinstance(created_data, dict):

                        new_case_id = created_data.get("id")

                        if new_case_id:
                            st.session_state.selected_case = new_case_id

                    st.rerun()

                except Exception as exc:

                    st.error(f"Unable to create case: {exc}")


st.divider()


# --------------------------------------------------
# EXISTING CLINICAL CASES
# --------------------------------------------------

st.subheader("📋 Existing Clinical Cases")

st.caption("Search and select an existing research case.")

if load_error:

    st.error(f"Unable to load clinical cases: {load_error}")

elif not cases:

    st.info(
        "No clinical cases found. Create your first research case above."
    )

else:

    col1, col2 = st.columns([2, 1])

    with col1:

        search_query = st.text_input(
            "Search Cases",
            placeholder="Search by title or clinical question...",
            key="case_search"
        )

    with col2:

        statuses = sorted({
            str(case.get("status", "unknown"))
            for case in cases
        })

        selected_status = st.selectbox(
            "Filter by Status",
            ["All"] + statuses
        )

    filtered_cases = []

    for case in cases:

        case_title = str(case.get("title", ""))
        case_question = str(case.get("clinical_question", ""))
        case_status = str(case.get("status", "unknown"))

        search_text = f"{case_title} {case_question}".lower()

        matches_search = (
            search_query.strip().lower() in search_text
        )

        matches_status = (
            selected_status == "All"
            or case_status == selected_status
        )

        if matches_search and matches_status:
            filtered_cases.append(case)

    st.caption(
        f"Showing {len(filtered_cases)} of {total_cases} cases"
    )

    for index, case in enumerate(filtered_cases):

        case_id = case.get("id")
        case_title = case.get("title", "Untitled Case")
        case_question = case.get(
            "clinical_question",
            "No research question available."
        )
        case_status = str(
            case.get("status", "unknown")
        )

        with st.container(border=True):

            title_col, status_col = st.columns([3, 1])

            with title_col:
                st.markdown(f"**{case_title}**")

            with status_col:

                if case_status == "approved":
                    st.success("Approved")

                elif case_status == "rejected":
                    st.error("Rejected")

                elif case_status == "review_pending":
                    st.warning("Pending Review")

                else:
                    st.info(case_status.replace("_", " ").title())

            st.write(case_question)

            st.caption(f"Case ID: {case_id}")

            if st.button(
                "Select Case",
                key=f"select_case_{case_id}_{index}",
                use_container_width=True
            ):

                st.session_state.selected_case = case_id
                st.rerun()

            if str(st.session_state.get("selected_case")) == str(case_id):
                st.info("Currently selected research case")


# --------------------------------------------------
# SELECTED CASE
# --------------------------------------------------

selected_case = st.session_state.get("selected_case")

if selected_case:

    st.divider()

    st.subheader("Selected Research Case")

    selected_record = next(
        (
            case for case in cases
            if str(case.get("id")) == str(selected_case)
        ),
        None
    )

    if selected_record:

        with st.container(border=True):

            st.markdown(
                f"**{selected_record.get('title', 'Untitled Case')}**"
            )

            st.caption(f"Case ID: {selected_case}")

            st.write(
                selected_record.get(
                    "clinical_question",
                    "No clinical question available."
                )
            )

    else:

        st.warning(
            "Selected case is not present in the currently loaded case list."
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Clinical Evidence AI | Clinical Case Management"
)
