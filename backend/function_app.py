import json
import azure.functions as func

from shared.database import get_connection
from shared.fee_service import calculate_payment_status


app = func.FunctionApp()


@app.route(
    route="students/{studentId}/fees",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def get_fee_details(req: func.HttpRequest) -> func.HttpResponse:

    student_id = req.route_params.get("studentId")

    if not student_id:
        return func.HttpResponse(
            json.dumps({"error": "StudentID is required"}),
            status_code=400,
            mimetype="application/json"
        )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                StudentID,
                Name,
                Email,
                Course,
                TotalFee,
                PaidAmount,
                DueDate
            FROM Students
            WHERE StudentID = ?
            """,
            student_id
        )

        row = cursor.fetchone()

        if row is None:
            return func.HttpResponse(
                json.dumps({"error": "Student not found"}),
                status_code=404,
                mimetype="application/json"
            )

        total_fee = float(row.TotalFee)
        paid_amount = float(row.PaidAmount)

        outstanding_amount = total_fee - paid_amount

        payment_status = calculate_payment_status(
            total_fee,
            paid_amount,
            row.DueDate
        )

        response = {
            "student_id": row.StudentID,
            "name": row.Name,
            "email": row.Email,
            "course": row.Course,
            "total_fee": total_fee,
            "paid_amount": paid_amount,
            "outstanding_amount": outstanding_amount,
            "due_date": row.DueDate.isoformat(),
            "payment_status": payment_status
        }

        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error"
            }),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

            
@app.route(
    route="fee-update/{studentId}",
    methods=["PUT"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def update_fee(req: func.HttpRequest) -> func.HttpResponse:

    student_id = req.route_params.get("studentId")

    if not student_id:
        return func.HttpResponse(
            json.dumps({"error": "StudentID is required"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        request_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json"
        )

    if "paid_amount" not in request_body:
        return func.HttpResponse(
            json.dumps({"error": "paid_amount is required"}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        paid_amount = float(request_body["paid_amount"])

        if paid_amount < 0:
            return func.HttpResponse(
                json.dumps({"error": "paid_amount cannot be negative"}),
                status_code=400,
                mimetype="application/json"
            )

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT TotalFee
            FROM Students
            WHERE StudentID = ?
            """,
            student_id
        )

        row = cursor.fetchone()

        if row is None:
            cursor.close()
            connection.close()

            return func.HttpResponse(
                json.dumps({"error": "Student not found"}),
                status_code=404,
                mimetype="application/json"
            )

        total_fee = float(row.TotalFee)

        if paid_amount > total_fee:
            cursor.close()
            connection.close()

            return func.HttpResponse(
                json.dumps({
                    "error": "paid_amount cannot exceed total fee"
                }),
                status_code=400,
                mimetype="application/json"
            )

        cursor.execute(
            """
            UPDATE Students
            SET PaidAmount = ?
            WHERE StudentID = ?
            """,
            paid_amount,
            student_id
        )

        connection.commit()

        cursor.close()
        connection.close()

        return func.HttpResponse(
            json.dumps({
                "message": "Fee record updated successfully",
                "student_id": student_id,
                "paid_amount": paid_amount
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error"
            }),
            status_code=500,
            mimetype="application/json"
        )