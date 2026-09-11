from datetime import date


def calculate_payment_status(total_fee, paid_amount, due_date):
    if paid_amount >= total_fee:
        return "Paid"

    if due_date < date.today():
        return "Overdue"

    return "Partially Paid"