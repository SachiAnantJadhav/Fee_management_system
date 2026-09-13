# Student Fee Management System

A cloud-ready student fee management system built with Streamlit, Azure Functions, Azure SQL Database, Microsoft Entra ID, Azure API Management, and Azure Logic Apps.

The system gives students a secure view of their fee records and gives administrators the ability to update payment information. Azure services provide the API gateway, authentication, automation, monitoring, and scalability needed for a production deployment.

## Features

- Student and administrator dashboards built with Streamlit
- Azure Functions API for retrieving and updating fee records
- Azure SQL Database schema for students and administrators
- Payment status calculation: `Paid`, `Partially Paid`, or `Overdue`
- Microsoft Entra ID authentication with `Administrator` and `Student` app roles
- Azure API Management integration for JWT validation, rate limiting, retries, and routing
- Logic App workflow design for overdue-fee email reminders
- Automated validation for invalid payment updates
- Application Insights monitoring support

## Architecture

<img width="2787" height="1641" alt="Blank diagram (1)" src="https://github.com/user-attachments/assets/eba05bc5-70a3-4e4b-86ef-5326900535d7" />

## Repository Layout

```text
.
├── api-management/
│   ├── api-definition.json       # API Management definition
│   └── policies.xml              # APIM policy location
├── backend/
│   ├── function_app.py           # Azure Functions HTTP endpoints
│   ├── host.json
│   ├── requirements.txt
│   └── shared/
│       ├── auth.py
│       ├── database.py
│       └── fee_service.py        # Payment status logic
├── database/
│   ├── schema.sql                # Students and Administrators tables
│   ├── seed.sql                  # Sample data
│   └── queries.sql
├── frontend/
│   ├── app.py                    # Streamlit entry point
│   ├── pages/
│   ├── services/
│   └── utils/
├── logic-app/
│   ├── README.md
│   └── workflow.json
├── tests/
├── requirements.txt              # Frontend dependencies
└── README.md
```

## Technology Stack

| Layer       | Technology                  | Responsibility                                   |
| ----------- | --------------------------- | ------------------------------------------------ |
| Frontend\*  | Streamlit                   | Student and administrator UI                     |
| API         | Azure Functions with Python | Fee retrieval, updates, and business logic       |
| Database    | Azure SQL Database          | Relational fee and user data                     |
| API gateway | Azure API Management        | Routing, JWT validation, throttling, and retries |
| Identity    | Microsoft Entra ID          | Authentication and app roles                     |
| Automation  | Azure Logic Apps            | Overdue-fee reminder workflow                    |
| Monitoring  | Azure Application Insights  | Requests, failures, logs, and response times     |
| Testing     | Pytest / Postman            | Automated and API-level verification             |

The frontend is included in the current repository and is organized as follows:

- `frontend/app.py` is the Streamlit entry point and routes users to the appropriate dashboard.
- `frontend/pages/student_dashboard.py` lets students retrieve their own fee details using the `student_id` claim from the access token.
- `frontend/pages/admin_dashboard.py` lets administrators retrieve a student's fee details, list students with pending dues, and update a student's paid amount.
- `frontend/services/auth.py` handles Microsoft Entra ID authorization-code login through MSAL.
- `frontend/services/api_client.py` sends bearer tokens and the APIM subscription key to the API gateway.
- `frontend/utils/session.py` reads token claims and resolves the user's `Administrator` or `Student` role.

The frontend enforces the dashboard experience based on the roles in the token. API authorization must still be enforced at APIM as described in the [Authorization Model](#authorization-model).

## Data Model

The database schema is in [`database/schema.sql`](database/schema.sql).

### `Students`

| Column       | Description                        |
| ------------ | ---------------------------------- |
| `StudentID`  | Primary key and student identifier |
| `Name`       | Student name                       |
| `Email`      | Reminder email address             |
| `Course`     | Academic course                    |
| `TotalFee`   | Total amount payable               |
| `PaidAmount` | Amount paid so far                 |
| `DueDate`    | Payment due date                   |

The schema enforces non-negative fees and prevents `PaidAmount` from exceeding `TotalFee`.

### `Administrators`

| Column    | Description        |
| --------- | ------------------ |
| `AdminID` | Primary key        |
| `Name`    | Administrator name |
| `Role`    | Administrator role |

## Payment Status

The backend calculates status in `backend/shared/fee_service.py`:

1. `PaidAmount >= TotalFee` returns `Paid`.
2. An unpaid record past its due date returns `Overdue`.
3. All other unpaid records return `Partially Paid`.

The API also returns `outstanding_amount`, calculated as:

```text
outstanding_amount = total_fee - paid_amount
```

## API

### Get Student Fee Details

```http
GET /api/students/{studentId}/fees
```

Example:

```http
GET /api/students/STU005/fees
```

Example response:

```json
{
  "student_id": "STU005",
  "name": "Kabir Verma",
  "email": "kabir@example.com",
  "course": "B.Tech CSE",
  "total_fee": 120000.0,
  "paid_amount": 100005.0,
  "outstanding_amount": 19995.0,
  "due_date": "2026-09-20",
  "payment_status": "Partially Paid"
}
```

### Update Student Fee

```http
PUT /api/fee-update/{studentId}
Content-Type: application/json
```

Request body:

```json
{
  "paid_amount": 100005
}
```

The update endpoint validates the JSON body, rejects negative values, rejects payments greater than the total fee, and returns `404` when the student does not exist.

### Get Students With Pending Dues

```http
GET /api/pending
```

The pending endpoint is intended for administrator use. It returns students whose fee records still have an outstanding balance, allowing the administrator dashboard to display a pending-dues table.

Example response:

```json
{
  "students": [
    {
      "student_id": "STU005",
      "name": "Kabir Verma",
      "email": "kabir@example.com",
      "course": "B.Tech CSE",
      "total_fee": 120000.0,
      "paid_amount": 100005.0,
      "outstanding_amount": 19995.0,
      "due_date": "2026-09-20",
      "payment_status": "Partially Paid"
    }
  ]
}
```

The current Streamlit administrator dashboard calls this route at `/pending`. Ensure that the deployed Function App and APIM configuration expose the route before using **Find Pending Dues**. The existing `backend/function_app.py` currently contains the fee-details and fee-update routes; the pending route still needs to be implemented or connected in the backend deployment.

### APIM URLs

The Streamlit API client uses the APIM base URL and the following gateway paths:

```text
GET https://<apim-host>/fees/students/{studentId}/fees
PUT https://<apim-host>/fees/fee-update/{studentId}
GET https://<apim-host>/fees/pending
```

Set `API_BASE_URL` to the deployed APIM API base URL, for example `https://<apim-host>/fees`, and set `APIM_SUBSCRIPTION_KEY` to the subscription key required by the gateway.

## Authorization Model

Configure these Microsoft Entra ID app roles:

| Operation                       | Administrator | Student |
| ------------------------------- | ------------- | ------- |
| Retrieve fee details            | Yes           | Yes     |
| View payment status             | Yes           | Yes     |
| View students with pending dues | Yes           | No      |
| Update fee record               | Yes           | No      |
| Administrative operations       | Yes           | No      |

The access token should contain the appropriate `roles` claim. APIM should validate the token issuer, signature, audience, and required role before forwarding protected requests to the Function App.

> The Functions routes use anonymous function authorization because authorization is intended to be enforced at the APIM gateway. Do not expose the Function App directly in production without an equivalent authentication boundary.

## Local Setup

### 1. Clone the repository

```powershell
git clone https://github.com/SachiAnantJadhav/Fee_management_system.git
cd Fee_management_system
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate
```

### 3. Install frontend dependencies

```powershell
pip install -r requirements.txt
```

Install backend dependencies separately when running Azure Functions locally:

```powershell
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

For the backend, set `SQL_CONNECTION_STRING` to an Azure SQL connection string. For the frontend, set the APIM API base URL, subscription key, and Microsoft Entra ID settings used by the Streamlit application.

Example PowerShell configuration for the current session:

```powershell
$env:SQL_CONNECTION_STRING = "<azure-sql-connection-string>"
$env:API_BASE_URL = "https://<apim-host>/fees"
$env:APIM_SUBSCRIPTION_KEY = "<apim-subscription-key>"
$env:TENANT_ID = "<tenant-id>"
$env:CLIENT_ID = "<frontend-client-id>"
$env:CLIENT_SECRET = "<frontend-client-secret>"
$env:REDIRECT_URI = "http://localhost:8501"
$env:AUTHORITY = "https://login.microsoftonline.com/<tenant-id>"
$env:API_SCOPE = "api://<api-application-id>/.default"
```

The frontend reads these values from environment variables or a local `.env` file. Keep client secrets, connection strings, subscription keys, and access tokens out of source control. The redirect URI must also be registered for the frontend application in Microsoft Entra ID.

Keep credentials, client secrets, connection strings, and access tokens out of source control. Use Function App settings or Azure Key Vault for deployed environments.

### 5. Initialize the database

Run the scripts in order using Azure SQL Query Editor, SQL Server Management Studio, or another SQL client:

```text
database/schema.sql
database/seed.sql
```

Verify the sample data:

```sql
SELECT COUNT(*) FROM Students;
```

### 6. Run the Streamlit frontend

```powershell
streamlit run frontend/app.py
```

Open the displayed local URL, sign in with Microsoft Entra ID, and use the dashboard associated with the `Administrator` or `Student` app role. The frontend redirects API requests through APIM and sends the bearer token in the `Authorization` header together with the `Ocp-Apim-Subscription-Key` header. Student accounts need a `student_id` claim in the access token to load their own fee record.

### 7. Run the Functions backend locally

From the `backend` directory, with Azure Functions Core Tools installed:

```powershell
cd backend
func start
```

The local Functions host normally serves routes below `http://localhost:7071/api`. When using APIM, configure the gateway backend to point to the deployed Function App rather than the local host.

## Azure Deployment Guide

1. Create a resource group and Azure SQL Database.
2. Run `database/schema.sql` and `database/seed.sql`.
3. Create a Python Azure Function App and deploy the `backend` directory.
4. Configure `SQL_CONNECTION_STRING` in Function App settings.
5. Create the Microsoft Entra ID API registration and assign the `Administrator` and `Student` app roles.
6. Import the API definition from `api-management/api-definition.json` into APIM.
7. Configure APIM policies for JWT validation, role checks, rate limiting, and retries.
8. Set the APIM backend to the Function App.
9. Set `APIM_BASE_URL` for the Streamlit deployment.
10. Create the Logic App recurrence, SQL query, foreach, and email actions described below.
11. Connect the Function App to Application Insights and verify request telemetry.

### Recommended APIM Policies

The supplied design calls for:

```xml
<rate-limit calls="5" renewal-period="60" />
```

This allows five requests per 60-second window and returns `429 Too Many Requests` after the limit is exceeded.

For transient backend failures, configure a retry policy for responses with status codes in the `500` range, with two retries and a one-second interval.

Use separate required-role checks for read and update operations. Both roles may read fee details, but only `Administrator` may update a fee record.

## Automated Reminder Workflow

The automated reminder workflow is deployed as **`fee-reminder-logic-app`**. It uses Azure Logic Apps with the **SendGrid** connector to send overdue-fee reminder emails.

The Logic App should use this sequence:

<img width="270" height="500" alt="WhatsApp Image 2026-09-11 at 1 14 24 PM" src="https://github.com/user-attachments/assets/a3fd5e07-b76c-4f04-9c70-6c6b48a4fa71" />

```text
Recurrence
	-> Execute SQL query for overdue students
	-> For each returned student
	-> Send an email reminder through SendGrid
```

The overdue query should select unpaid records whose `DueDate` is earlier than the current date. Configure SendGrid with the verified sender address and map each student's `Email` field to the recipient address.

<img width="270" height="360" alt="WhatsApp Image 2026-09-11 at 1 12 55 PM" src="https://github.com/user-attachments/assets/48171b61-0749-420b-9df5-f61f77f30586" />

## Testing Checklist

| Scenario                              | Expected result                             |
| ------------------------------------- | ------------------------------------------- |
| Administrator GET                     | `200 OK`                                    |
| Student GET                           | `200 OK`                                    |
| Administrator pending dues GET        | `200 OK` with matching student records      |
| Administrator PUT                     | `200 OK` and database value updated         |
| Student PUT                           | `403 Forbidden` at APIM                     |
| Missing or invalid token              | `401 Unauthorized`                          |
| Unknown student                       | `404 Not Found`                             |
| Invalid payment amount                | `400 Bad Request`                           |
| More than five requests in 60 seconds | `429 Too Many Requests`                     |
| Logic App run                         | Reminder email sent to each overdue student |
| Application Insights                  | Requests and failures visible               |

Run the Python tests from the repository root with:

```powershell
pytest
```

Use Postman for token-based APIM testing and to demonstrate the role, rate-limit, and update flows.

## Monitoring and Reliability

Application Insights should be used to monitor:

- Request count and response time
- Failed requests and HTTP status codes
- Function logs and exceptions
- APIM throttling and backend failures
- Logic App workflow runs

Azure Functions, Azure SQL Database, APIM, and Logic Apps are independently managed services. This separation allows API traffic, persistent data, and reminder processing to scale independently. APIM retries can reduce the impact of temporary backend failures, while Application Insights provides the telemetry needed to diagnose persistent issues.

## Security Notes

- Keep secrets and connection strings in environment variables, Function App settings, or Azure Key Vault.
- Require Microsoft Entra ID access tokens at the APIM boundary.
- Validate token issuer, audience, signature, and role claims.
- Keep update operations restricted to administrators.
- Avoid exposing the Function App endpoint directly when APIM is the intended security boundary.
- Add audit logging for administrator changes before production use.

## Future Improvements

- Add interactive Microsoft Entra ID login to the Streamlit frontend.
- Store production secrets in Azure Key Vault.
- Add CI/CD with GitHub Actions or Azure DevOps.
- Add pagination and search for large student datasets.
- Add audit history for payment updates.
- Add centralized alerting through Azure Monitor.
- Add API versioning and integration tests.
- Use Azure Service Bus for more resilient notification processing.
