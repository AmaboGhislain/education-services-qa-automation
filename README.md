# Education Services QA Automation Project

## Overview

This project is a Software Quality Assurance (QA) automation portfolio focused on testing digital services used by educational institutions.

It uses Python, pytest, Requests, Selenium, FastAPI, SQLAlchemy, and SQLite to practise API testing, browser automation, data validation, database integration, error handling, and automated test reporting.

The project includes a database-backed Education Services API for registering students and recording and retrieving examination results.

## Project Objectives

* Test student-record APIs and data validation.
* Validate examination scores and illustrative grading rules.
* Test school-fee payment validation, payment statuses, and duplicate-payment detection.
* Automate browser-based login scenarios.
* Test API responses, error handling, and data types.
* Verify database-backed student and examination-result operations.
* Generate HTML test reports.
* Prepare for database-backed school-fee and teacher-salary systems.
* Progress toward payment-provider sandbox testing and continuous integration.

## Technology Stack

* **Python:** Test automation and application development.
* **pytest:** Test execution, assertions, and parameterized tests.
* **Requests:** HTTP API testing.
* **Selenium:** Browser automation.
* **FastAPI:** Education Services API development.
* **SQLAlchemy:** Database access and ORM.
* **SQLite:** Persistent local database storage.
* **Pydantic:** Request-data validation.
* **Uvicorn:** Local API server.
* **httpx:** API test-client dependency.
* **pytest-html:** HTML test reporting.
* **Git and GitHub:** Version control and collaboration.

## Project Structure

```text
software-testing-project/
├── api_tests/
│   ├── test_education_api.py
│   ├── test_results_api.py
│   ├── test_school_fees.py
│   ├── test_students_api.py
│   └── test_users_api.py
├── education_api/
│   ├── __init__.py
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   └── models.py
├── data/
│   └── education.db       # Local database; not committed
├── pages/
│   ├── __init__.py
│   └── login_page.py
├── Test/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_google.py
│   └── test_login.py
├── reports/               # Generated reports; not committed
├── .vscode/
├── .gitignore
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

The SQLite database is generated locally and is excluded from version control. The structure above describes the expected project layout; generated files and folders may not appear in a fresh clone until the application or tests are run.

## Prerequisites

* Python installed.
* Git installed.
* Visual Studio Code recommended.
* Internet access for tests that contact external APIs or websites.

## Installation

Clone the GitHub repository:

```powershell
git clone https://github.com/AmaboGhislain/education-services-qa-automation.git
cd education-services-qa-automation
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running the Automated Tests

Run the entire test suite:

```powershell
python -m pytest -v
```

Run API tests:

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

Open the generated HTML report in a browser to review the test results.

## Running the Education Services API

Start the local API server from the project root:

```powershell
python -m uvicorn education_api.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

Check the health endpoint:

http://127.0.0.1:8000/health

The API currently provides these endpoints:

| Method | Endpoint                         | Purpose                      |
| ------ | -------------------------------- | ---------------------------- |
| GET    | `/health`                        | Check API availability       |
| POST   | `/students`                      | Register a student           |
| GET    | `/students`                      | List registered students     |
| POST   | `/results`                       | Record an examination result |
| GET    | `/students/{student_id}/results` | Retrieve a student's results |

### Database

The application uses SQLite for persistent local storage. The database file is located at `data/education.db` and contains student and examination-result tables.

The database tables can be initialized with:

```powershell
python -m education_api.init_db
```

The application also creates the tables during startup.

The automated tests in `api_tests/test_education_api.py` use an isolated in-memory SQLite database. This prevents test records from being mixed with the application's persistent local records.

## Current Test Coverage

The project includes automated checks for:

* Student-record retrieval and data validation.
* Examination-result retrieval and illustrative grading rules.
* School-fee amount and payment-status validation.
* Duplicate-payment detection logic.
* API creation, retrieval, updates, deletion, errors, and data types.
* Browser-based successful and unsuccessful login scenarios.
* Education API health checks.
* Successful student registration.
* Duplicate student-number rejection.
* Examination-result creation and retrieval.
* Invalid examination scores below zero or above 100.
* Results submitted for nonexistent students.

**Latest full-suite baseline:** 65 tests passed in 56.65 seconds, with one deprecation warning. This is the result from the development environment on 13 October 2026; test results may vary with dependency versions and external service availability.

## Current Limitations

This project is a work in progress.

* Some API tests use JSONPlaceholder, a public demonstration API.
* Some school-fee and grading tests validate local test logic rather than a live school application.
* The Education Services API uses a local SQLite database; it is not yet connected to a production school database.
* No real payment-provider sandbox has been integrated yet.
* Teacher-salary and payroll API functionality remains planned.
* Authentication, role-based access control, and production security hardening remain future improvements.
* Sample grading rules are illustrative and must be adapted to each institution's official policies.

Only fictional student data should be used for demonstrations. Do not commit database files, real student records, payroll data, passwords, API tokens, payment credentials, or other secrets.

## Planned Improvements

1. Expand automated testing of the student-results API, including persistence and boundary cases.
2. Develop database-backed school-fee payment functionality.
3. Develop teacher-salary and payroll validation functionality.
4. Integrate a payment-provider sandbox using protected environment variables.
5. Add security, authentication, authorization, and access-control tests.
6. Add continuous integration using GitHub Actions.
7. Improve test reporting, coverage measurement, and regression testing.
8. Evaluate PostgreSQL for a future multi-user deployment.

## Author

**Amabo Ghislain**

Software Testing | QA Automation | Educational Systems

This project demonstrates practical learning and development in software quality assurance, test automation, API validation, and database-backed educational services.
