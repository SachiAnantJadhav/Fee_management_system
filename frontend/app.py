import streamlit as st

from services.auth import get_login_url, process_login, logout
from utils.session import get_role, get_username
from pages.admin_dashboard import show_admin_dashboard
from pages.student_dashboard import show_student_dashboard


st.set_page_config(
    page_title="Fee Management System",
    page_icon="💰",
    layout="wide"
)


# =========================================================
# PROCESS MICROSOFT LOGIN
# =========================================================

if "access_token" not in st.session_state:

    process_login()


# =========================================================
# LOGIN PAGE
# =========================================================

if "access_token" not in st.session_state:

    st.title("Fee Management System")

    st.write(
        "Secure student fee management using Microsoft Entra ID."
    )

    login_url = get_login_url()

    st.link_button(
        "Login with Microsoft",
        login_url
    )

    st.stop()


# =========================================================
# GET USER ROLE
# =========================================================

role = get_role()
username = get_username()


# =========================================================
# INVALID ROLE
# =========================================================

if role is None:

    st.error(
        "Your account does not have a valid application role."
    )

    if st.button("Logout"):
        logout()

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("Fee Management")

    st.write(
        f"**User:** {username}"
    )

    st.write(
        f"**Role:** {role}"
    )

    st.divider()

    if st.button("Logout"):

        logout()


# =========================================================
# ROLE-BASED DASHBOARD
# =========================================================

if role == "Administrator":

    show_admin_dashboard()

elif role == "Student":

    show_student_dashboard()