import os
import msal
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORITY = os.getenv("AUTHORITY")
API_SCOPE = os.getenv("API_SCOPE")


def get_msal_app():

    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )


def get_login_url():

    app = get_msal_app()

    return app.get_authorization_request_url(
        scopes=[API_SCOPE],
        redirect_uri=REDIRECT_URI,
        prompt="select_account"
    )


def process_login():

    if "code" not in st.query_params:
        return False

    code = st.query_params["code"]

    app = get_msal_app()

    result = app.acquire_token_by_authorization_code(
        code,
        scopes=[API_SCOPE],
        redirect_uri=REDIRECT_URI
    )

    if "access_token" not in result:
        st.error(
            result.get(
                "error_description",
                "Authentication failed."
            )
        )
        return False

    st.session_state["access_token"] = result["access_token"]

    return True


def logout():

    keys_to_remove = [
        "access_token",
        "student_id",
        "role"
    ]

    for key in keys_to_remove:

        if key in st.session_state:
            del st.session_state[key]

    st.query_params.clear()

    st.rerun()