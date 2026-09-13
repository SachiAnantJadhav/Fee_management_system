import streamlit as st

from services.api_client import APIClient
from utils.session import get_claims


def show_student_dashboard():

    st.title("Student Dashboard")

    st.write("View your fee details and payment status.")

    token = st.session_state.get("access_token")

    if not token:
        st.error("Authentication token not found.")
        return

    claims = get_claims()

    student_id = claims.get("student_id")

    if not student_id:

        st.error(
            "Student ID was not found in the authentication token."
        )

        st.info(
            "Add the Student ID as a claim in the student's JWT."
        )

        return

    api = APIClient(token)

    st.write(f"Student ID: **{student_id}**")

    if st.button("View My Fee Details"):

        response = api.get_student_fees(student_id)

        if response.status_code == 200:

            data = response.json()

            st.success("Fee details retrieved successfully.")

            col1, col2 = st.columns(2)

            with col1:

                st.write("### Student Information")

                st.write(
                    "**Name:**",
                    data["name"]
                )

                st.write(
                    "**Email:**",
                    data["email"]
                )

                st.write(
                    "**Course:**",
                    data["course"]
                )

            with col2:

                st.write("### Fee Information")

                st.write(
                    "**Total Fee:**",
                    data["total_fee"]
                )

                st.write(
                    "**Paid Amount:**",
                    data["paid_amount"]
                )

                st.write(
                    "**Outstanding Amount:**",
                    data["outstanding_amount"]
                )

                st.write(
                    "**Due Date:**",
                    data["due_date"]
                )

                st.write(
                    "**Payment Status:**",
                    data["payment_status"]
                )

        else:

            st.error(
                f"Request failed: {response.status_code}"
            )

            try:
                st.json(response.json())
            except Exception:
                st.write(response.text)