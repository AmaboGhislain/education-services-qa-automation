# Education Services QA Automation Project

## Overview

This project is a Software Quality Assurance (QA) automation portfolio focused on testing digital services used by educational institutions.

It uses Python, pytest, Requests, Selenium, FastAPI, SQLAlchemy, and SQLite to practise API testing, browser automation, data validation, database integration, error handling, and automated test reporting.

The project includes a database-backed Education Services API for student registration, examination results, and simulated school-fee payment workflows.

## Project Objectives

- Test student-record APIs and data validation.
- Validate examination scores and illustrative grading rules.
- Test school-fee payment creation, retrieval, and status handling.
- Verify duplicate payment-reference detection.
- Test simulated successful and failed payment verification.
- Check that payment verification rejects missing or incorrect API keys.
- Automate browser-based login scenarios using Selenium.
- Verify database-backed student and examination-result operations.
- Generate self-contained HTML test reports.
- Develop a foundation for future teacher-salary and payroll testing.
- Prepare for payment-provider sandbox testing and continuous integration.

## Technology Stack

- **Python:** Test automation and application development.
- **pytest:** Test execution, assertions, fixtures, and parameterized tests.
- **Requests:** HTTP API testing.
- **Selenium:** Browser automation.
- **FastAPI:** Education Services API development.
- **SQLAlchemy:** Database access and ORM.
- **SQLite:** Local database storage.
- **Pydantic:** Request-data validation.
- **Uvicorn:** Local API server.
- **HTTPX / HTTPX2:** HTTP client and test-client compatibility dependencies.
- **pytest-html:** HTML test reporting.
- **Git and GitHub:** Version control and collaboration.

## Project Structure

```text
software-testing-project/
├── api_tests/
│   ├── test_education_api.py
│   ├── test_results_api.py
│   ├── test_school_fees.py
│   ├── test_students_api.py
│   ├── test_users_api.py
│   └── test_payment_api.py
├── education_api/
│   ├── __init__.py
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   └── models.py
├── data/                 # Local database; excluded from Git
├── pages/
│   ├── __init__.py
│   └── login_page.py
├── Test/
│   ├── test_calculator.py
│   ├── test_google.py
│   └── test_login.py
├── reports/              # Generated reports; excluded from Git
├── .vscode/
├── .gitignore
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Prerequisites

- Python installed.
- Git installed.
- Visual Studio Code recommended.
- Internet access for tests that contact external websites or APIs.

## Installation

Clone the repository:

```powershell
git clone https://github.com/AmaboGhislain/education-services-qa-automation.git
cd education-services-qa-automation
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running the Automated Tests

Run the full test suite:

```powershell
python -m pytest -v
```

Run the API tests:

```powershell
python -m pytest api_tests -v
```

Run browser and other tests:

```powershell
python -m pytest Test -v
```

Generate an HTML test report:

```powershell
New-Item -ItemType Directory -Force reports
python -m pytest -v --html=reports/full_test_report.html --self-contained-html
```

Open `reports/full_test_report.html` in a browser to review the results.

## Running the Education Services API

Start the local API server from the project root:

```powershell
python -m uvicorn education_api.main:app --reload
```

Interactive API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health

### API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API availability |
| POST | `/students` | Register a student |
| GET | `/students` | List registered students |
| POST | `/results` | Record an examination result |
| GET | `/students/{student_id}/results` | Retrieve a student's results |
| POST | `/payments` | Create a school-fee payment record |
| GET | `/payments/{payment_id}` | Retrieve a payment |
| GET | `/students/{student_id}/payments` | Retrieve a student's payments |
| POST | `/payments/{payment_id}/verify` | Simulate verification of a pending payment |

Consult `/docs` for the current request and response schemas.

## Database

The application uses SQLite for local persistent storage. The database file is located at `data/education.db`.

Initialize the database with:

```powershell
python -m education_api.init_db
```

The application also initializes its tables during startup.

API tests use an isolated in-memory SQLite database to prevent test records from mixing with local application data.

The local database file is excluded from version control. Use fictional data for testing and demonstrations.

## School-Fee Payment Testing

The simulated payment workflow supports:

- Payment creation and retrieval.
- Positive-amount validation.
- Currency validation.
- Rejection of payments for nonexistent students.
- Duplicate payment-reference detection.
- Pending, successful, and failed payment statuses.
- Rejection of invalid verification outcomes.
- Prevention of repeated verification.
- Rejection of verification requests with missing or incorrect simulator API keys.
- Confirmation that rejected verification requests do not change a payment's status.

### Simulated Payment Verification Security

The verification endpoint requires the `X-Simulator-Key` HTTP header.

For local development, the application uses the `SIMULATOR_API_KEY` environment variable when configured. Otherwise, it falls back to a development-only default.

To configure your own local development key in PowerShell before starting the API:

```powershell
$env:SIMULATOR_API_KEY = "replace-with-your-local-test-key"
python -m uvicorn education_api.main:app --reload
```

Use the same value in the `X-Simulator-Key` header when testing the verification endpoint.

**Security note:** The fallback key is for local development only. Do not use it in a deployed application. Never commit real secrets, API keys, payment credentials, or sensitive student information to GitHub.

The verification endpoint is a simulator. It accepts a verification outcome from a request authenticated with the simulator key; it does not independently verify transactions with a real payment provider. Production payment processing would require provider-side verification, authenticated callbacks, secure secret management, and additional controls.

## Current Test Coverage

The project includes automated tests for:

- Student registration and record retrieval.
- Student-number validation and duplicate detection.
- Examination-result creation and retrieval.
- Examination-score boundary validation.
- Payment amount, currency, and reference validation.
- Payment creation and retrieval.
- Simulated payment verification.
- Invalid and repeated payment-verification attempts.
- Missing and incorrect simulator API keys.
- Education API health checks.
- Browser-based login scenarios.
- API error handling and response validation.

### Latest Regression Test Result

**86 tests passed with no warnings** in the latest reported full-suite run.

Test results may vary with code changes, dependency versions, browser configuration, and external service availability. Run the test suite locally to verify the current state.

## Current Limitations

This project is a work in progress.

- Some tests use public demonstration APIs or external websites.
- Some grading and school-fee tests validate local application logic rather than a live school system.
- The Education Services API uses a local SQLite database and is not connected to a production school database.
- The payment-verification workflow is simulated; no real payment-provider sandbox has been integrated.
- Teacher-salary and payroll API functionality remains planned.
- Production authentication, authorization, role-based access control, and security hardening remain future improvements.
- Grading rules are illustrative and must be adapted to each institution's official policies.

## Planned Improvements

1. Expand student-results API testing, including persistence and boundary cases.
2. Improve database-backed school-fee payment functionality.
3. Develop teacher-salary and payroll validation functionality.
4. Integrate a payment-provider sandbox using protected environment variables.
5. Add authentication, authorization, and access-control tests.
6. Add continuous integration using GitHub Actions.
7. Improve reporting and code-coverage measurement.
8. Evaluate PostgreSQL for a future multi-user deployment.

## Author

**Amabo Ghislain**

Software Testing | QA Automation | Educational Systems

This project demonstrates practical learning and development in software quality assurance, test automation, API validation, simulated payment security, and database-backed educational services.