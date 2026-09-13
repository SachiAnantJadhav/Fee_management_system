import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

APIM_SUBSCRIPTION_KEY = os.getenv("APIM_SUBSCRIPTION_KEY")


class APIClient:

    def __init__(self, token):

        self.token = token

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Ocp-Apim-Subscription-Key": APIM_SUBSCRIPTION_KEY,
            "Content-Type": "application/json"
        }

    def get_student_fees(self, student_id):

        url = f"{API_BASE_URL}/students/{student_id}/fees"

        response = requests.get(
            url,
            headers=self.headers,
            timeout=30
        )

        return response

    def get_pending_students(self):

        url = f"{API_BASE_URL}/pending"

        response = requests.get(
            url,
            headers=self.headers,
            timeout=30
        )

        return response

    def update_fee(self, student_id, paid_amount):

        url = f"{API_BASE_URL}/fee-update/{student_id}"

        payload = {
            "paid_amount": paid_amount
        }

        response = requests.put(
            url,
            headers=self.headers,
            json=payload,
            timeout=30
        )

        return response