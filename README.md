# Education Services QA Automation Project

[![API tests](https://github.com/AmaboGhislain/education-services-qa-automation/actions/workflows/tests.yml/badge.svg)](https://github.com/AmaboGhislain/education-services-qa-automation/actions/workflows/tests.yml)
A Python QA automation portfolio for testing education-related APIs and workflows. The project includes a database-backed FastAPI application, API tests, browser tests, and examples of validation and simulated payment verification.

## Project objectives

- Practise API testing with pytest, including status codes, response data, validation errors, and reusable test helpers.
- Test student records and examination results.
- Test school-fee and teacher-salary payment workflows.
- Exercise duplicate detection and payment-verification rules.
- Practise Selenium browser automation.
- Generate self-contained HTML test reports.
- Build experience with Git and GitHub.

## Technology

- Python and pytest
- FastAPI and Pydantic
- SQLAlchemy and SQLite
- HTTPX and Requests
- Selenium
- pytest-html
- Uvicorn

## Project structure

```text
software-testing-project/
├── api_tests/
│   ├── test_education_api.py
│   ├── test_payment_api.py
│   ├── test_results_api.py
│   ├── test_salary_payment_api.py
│   ├── test_school_fees.py
│   ├── test_students_api.py
│   └── test_users_api.py
├── education_api/
│   ├── __init__.py
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   └── models.py
├── pages/
│   ├── __init__.py
│   └── login_page.py
├── Test/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_google.py
│   └── test_login.py
├── reports/                 # Generated reports; excluded from Git
├── data/                    # Local SQLite database; excluded from Git
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup

Requirements: Python and Git. Visual Studio Code is optional.

Create and activate a virtual environment in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run tests

Run the full test suite:

```powershell
python -m pytest -v
```

Run the API tests:

```powershell
python -m pytest api_tests -v
```

Run the browser and other tests:

```powershell
python -m pytest Test -v
```

Generate a self-contained HTML report:

```powershell
New-Item -ItemType Directory -Force reports
python -m pytest -v --html=reports/full_test_report.html --self-contained-html
```

Open `reports/full_test_report.html` in a browser to review the results. Test totals can change as tests are added; the latest run output is the source of the current count.

Some tests use external demonstration services or websites and may require an internet connection.

## Run the Education Services API

From the project root, start the local API server:

```powershell
python -m uvicorn education_api.main:app --reload
```

Open the interactive API documentation at <http://127.0.0.1:8000/docs>.

Health check: <http://127.0.0.1:8000/health>

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check that the API is running |
| POST | `/students` | Create a student record |
| GET | `/students` | List student records |
| POST | `/results` | Create an examination result |
| GET | `/students/{student_id}/results` | List a student's results |
| POST | `/payments` | Create a school-fee payment |
| GET | `/payments/{payment_id}` | Retrieve a school-fee payment |
| GET | `/students/{student_id}/payments` | List a student's school-fee payments |
| POST | `/payments/{payment_id}/verify` | Verify a pending school-fee payment |
| POST | `/teachers` | Create a teacher record |
| GET | `/teachers` | List teacher records |
| GET | `/teachers/{teacher_id}` | Retrieve a teacher record |
| POST | `/salary-payments` | Create a salary payment |
| GET | `/salary-payments/{salary_payment_id}` | Retrieve a salary payment |
| GET | `/teachers/{teacher_id}/salary-payments` | List a teacher's salary payments |
| POST | `/salary-payments/{salary_payment_id}/verify` | Verify a pending salary payment |

Consult `/docs` for the current request and response schemas.

## Database

The API uses SQLite for local persistent storage. The database file is `data/education.db`.

Initialize the database manually if needed:

```powershell
python -m education_api.init_db
```

The API also creates its tables during startup. API tests use an isolated in-memory SQLite database so test data does not mix with the local database.

Use fictional data for testing and demonstrations.

## Payment verification

School-fee and teacher-salary payment verification are simulated. Verification requests must include the `X-Simulator-Key` header and an outcome of `SUCCESS` or `FAILED`. A payment can only be verified while its status is `PENDING`.

For local development, the API reads the simulator key from the `SIMULATOR_API_KEY` environment variable. If it is not set, a development-only default is used.

Set a local key in PowerShell before starting the API:

```powershell
$env:SIMULATOR_API_KEY = "replace-with-your-local-test-key"
python -m uvicorn education_api.main:app --reload
```

Use the same value in the `X-Simulator-Key` header when testing verification.

The simulator does not contact or independently verify transactions with a payment provider. A production payment integration would need provider-side verification, secure secret management, and additional security controls. Do not use the development default in a deployed application or commit real credentials, API keys, or sensitive student data to GitHub.

## Test coverage

The automated tests cover:

- Student and teacher record creation and retrieval.
- Examination-result creation, retrieval, and score validation.
- School-fee payment creation, retrieval, validation, and duplicate references.
- Teacher-salary payment creation, retrieval, listing, validation, and duplicate references.
- Successful and failed payment verification.
- Invalid and repeated verification attempts.
- Missing and incorrect simulator API keys.
- API error responses and browser-based scenarios.

## Current limitations

- The API uses a local SQLite database and is not connected to a production school system.
- Payment verification is simulated and does not integrate with a payment-provider sandbox.
- Some tests depend on public demonstration APIs or external websites.
- Authentication, authorization, and role-based access control for application users are not implemented.
- Grading rules in the project are illustrative and should be adapted to an institution's official policies.

## Future improvements

- Add authentication, authorization, and access-control tests.
- Add continuous integration with GitHub Actions.
- Expand test reporting and add code-coverage measurement.
- Evaluate PostgreSQL for a future multi-user deployment.
- Integrate a payment-provider sandbox using protected environment variables.

## Author

**Amabo Ghislain**

Software Testing | QA Automation | Educational Systems