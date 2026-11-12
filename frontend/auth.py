import streamlit as st

from frontend.api_client import APIClient


def login_page():

    st.title("🧬 Clinical Evidence AI")

    st.subheader("Welcome Back")

    with st.form("login_form"):

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Sign In",
            use_container_width=True
        )

        if submitted:

            try:

                client = APIClient()

                result = client.post(
                    "/auth/login",
                    {
                        "email": email,
                        "password": password
                    }
                )

                st.session_state.token = (
                    result["access_token"]
                )

                profile = APIClient(
                    st.session_state.token
                ).get("/auth/me")

                st.session_state.user = profile
                st.session_state.authenticated = True

                st.rerun()

            except Exception as exc:

                st.error(f"Login failed: {exc}")


def logout():

    for key in [
        "token",
        "user",
        "authenticated",
        "selected_case",
        "workflow_result"
    ]:

        st.session_state.pop(key, None)

    st.rerun()