import json
import streamlit as st
from services.api_client import APIClient


def show_admin_dashboard():

    st.title("Administrator Dashboard")

    st.write("Manage student fee information.")

    token = st.session_state.get("access_token")

    if not token:
        st.error("Authentication token not found.")
        return

    api = APIClient(token)

    # =========================================================
    # 1. GET STUDENT FEE DETAILS
    # =========================================================

    st.header("Student Fee Details")

    student_id = st.text_input(
        "Enter Student ID",
        placeholder="Example: STU005"
    )

    if st.button("Get Student Details"):

        if not student_id:
            st.warning("Please enter a Student ID.")

        else:

            response = api.get_student_fees(student_id)

            if response.status_code == 200:

                data = response.json()

                st.success("Student details retrieved successfully.")

                col1, col2 = st.columns(2)

                with col1:

                    st.write("**Student ID:**", data["student_id"])
                    st.write("**Name:**", data["name"])
                    st.write("**Email:**", data["email"])
                    st.write("**Course:**", data["course"])

                with col2:

                    st.write("**Total Fee:**", data["total_fee"])
                    st.write("**Paid Amount:**", data["paid_amount"])
                    st.write(
                        "**Outstanding Amount:**",
                        data["outstanding_amount"]
                    )
                    st.write("**Due Date:**", data["due_date"])
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

    st.divider()

    # =========================================================
    # 2. FIND STUDENTS WITH PENDING DUES
    # =========================================================

    st.header("Students With Pending Dues")

    if st.button("Find Pending Dues"):

        response = api.get_pending_students()

        if response.status_code == 200:

            data = response.json()

            # Get the students list from the API response
            students = data.get("students", [])

            if students:

                # If students are returned as JSON strings, convert them to dictionaries
                formatted_students = []

                for student in students:

                    if isinstance(student, str):
                        try:
                            student = json.loads(student)
                        except json.JSONDecodeError:
                            continue

                    formatted_students.append({
                        "Student ID": student.get("student_id", ""),
                        "Name": student.get("name", ""),
                        "Email": student.get("email", ""),
                        "Course": student.get("course", ""),
                        "Total Fee": student.get("total_fee", 0),
                        "Paid Amount": student.get("paid_amount", 0),
                        "Outstanding Amount": student.get(
                            "outstanding_amount",
                            student.get("total_fee", 0) - student.get("paid_amount", 0)
                        ),
                        "Due Date": student.get("due_date", ""),
                        "Payment Status": student.get(
                            "payment_status",
                            "Pending"
                        )
                    })

                # Display students in a clean table
                if formatted_students:

                    st.dataframe(
                        formatted_students,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info("No students with pending dues found.")

            else:

                st.success("No students have pending dues.")

        else:

            st.error(
                f"Request failed: {response.status_code}"
            )

            try:
                st.json(response.json())
            except Exception:
                st.write(response.text)

    st.divider()

    # =========================================================
    # 3. UPDATE FEE
    # =========================================================

    st.header("Update Student Fee")

    update_student_id = st.text_input(
        "Student ID",
        key="update_student_id",
        placeholder="Example: STU005"
    )

    paid_amount = st.number_input(
        "Paid Amount",
        min_value=0.0,
        step=1000.0,
        key="paid_amount"
    )

    if st.button("Update Fee"):

        if not update_student_id:

            st.warning("Please enter a Student ID.")

        else:

            response = api.update_fee(
                update_student_id,
                paid_amount
            )

            if response.status_code == 200:

                st.success(
                    "Fee record updated successfully."
                )

                st.json(response.json())

            else:

                st.error(
                    f"Update failed: {response.status_code}"
                )

                try:
                    st.json(response.json())
                except Exception:
                    st.write(response.text)