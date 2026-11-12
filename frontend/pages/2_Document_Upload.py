
import streamlit as st
from frontend.api_client import APIClient
from frontend.sidebar import render_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Document Upload | Clinical Evidence AI",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: #172b4d;
}

.upload-info {
    padding: 16px;
    background: #eaf1fb;
    border-left: 4px solid #244d7c;
    border-radius: 8px;
    margin-bottom: 15px;
}

.stButton button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------
if not st.session_state.get("authenticated", False):
    st.warning("Please login to continue.")
    st.stop()

token = st.session_state.get("token")

if not token:
    st.error("Authentication token not found. Please login again.")
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
st.title("📄 Document Upload")
st.caption(
    "Upload clinical research documents for evidence extraction "
    "and AI-powered analysis."
)

st.divider()


# --------------------------------------------------
# SELECT CLINICAL CASE
# --------------------------------------------------
st.subheader("1. Select Clinical Case")

cases = []

try:
    response = client.get("/cases/")
    cases = response.get("data", response)

    if isinstance(cases, dict):
        cases = cases.get("items", [])

    if not isinstance(cases, list):
        cases = []

except Exception as e:
    st.error(f"Unable to load clinical cases: {e}")


case_id = None

if cases:
    case_options = {}

    for case in cases:
        if isinstance(case, dict):
            current_id = case.get("id") or case.get("case_id")
            current_title = case.get("title", "Untitled Case")

            if current_id is not None:
                case_options[
                    f"{current_title} (ID: {current_id})"
                ] = str(current_id)

    if case_options:
        selected_case = st.session_state.get("selected_case")

        option_labels = list(case_options.keys())
        default_index = 0

        if selected_case is not None:
            for index, label in enumerate(option_labels):
                if case_options[label] == str(selected_case):
                    default_index = index
                    break

        selected_label = st.selectbox(
            "Choose a clinical case",
            option_labels,
            index=default_index
        )

        case_id = case_options[selected_label]

    else:
        st.warning("No valid clinical cases found.")

else:
    st.info("No cases available. Enter a Case ID manually.")
    case_id = st.text_input("Clinical Case ID")


st.divider()


# --------------------------------------------------
# DOCUMENT UPLOAD
# --------------------------------------------------
st.subheader("2. Upload Clinical Documents")

st.markdown("""
<div class="upload-info">
<strong>Supported formats:</strong> PDF, TXT and Markdown (.md)<br>
Upload research papers, clinical guidelines, evidence documents,
or other relevant clinical resources.
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Choose your clinical documents",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True
)


# --------------------------------------------------
# UPLOAD ACTION
# --------------------------------------------------
if uploaded_files:
    st.write("### Selected Documents")

    for file in uploaded_files:
        st.write(f"📄 {file.name} — {file.size / 1024:.2f} KB")

    if st.button(
        "Upload Documents",
        type="primary",
        use_container_width=True
    ):
        if not case_id:
            st.error("Please select or enter a valid Clinical Case ID.")

        else:
            progress = st.progress(0)
            success_count = 0
            failed_files = []

            for index, uploaded_file in enumerate(uploaded_files):
                try:
                    uploaded_file.seek(0)

                    result = client.upload(
                        f"/documents/upload/{case_id}",
                        uploaded_file
                    )

                    success_count += 1

                    st.success(
                        f"Uploaded successfully: {uploaded_file.name}"
                    )

                except Exception as e:
                    failed_files.append(uploaded_file.name)
                    st.error(
                        f"Upload failed for {uploaded_file.name}: {e}"
                    )

                progress.progress(
                    (index + 1) / len(uploaded_files)
                )

            st.divider()

            if success_count:
                st.success(
                    f"{success_count} document(s) uploaded successfully."
                )

            if failed_files:
                st.warning(
                    f"{len(failed_files)} document(s) could not be uploaded."
                )


# --------------------------------------------------
# UPLOAD GUIDELINES
# --------------------------------------------------
st.divider()

st.subheader("3. Upload Guidelines")

st.markdown("""
- Upload documents relevant to the selected clinical case.
- Supported formats are PDF, TXT and MD.
- Verify that the correct clinical case is selected.
- Use readable and valid documents.
- Avoid uploading unrelated or duplicate documents.
""")

st.info(
    "Uploaded documents will be used by the backend document "
    "processing and evidence retrieval workflow."
)

st.caption(
    "Clinical Evidence AI | Document Upload Module"
)
