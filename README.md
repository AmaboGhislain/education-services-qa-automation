# Education Services QA Automation Project

## Overview

This project is a software quality assurance (QA) automation portfolio focused on testing digital services used by educational institutions.

It uses Python, pytest, Requests, and Selenium to practise API testing, browser automation, data validation, error handling, and test reporting.

## Project Objectives

* Test student record APIs.
* Validate examination results and sample grading rules.
* Test school-fee payment validation, payment statuses, and duplicate-payment detection.
* Automate browser-based login scenarios.
* Test API responses, error handling, and data types.
* Generate HTML test reports.
* Extend the project toward database integration and payment-provider sandbox testing.

## Technology Stack

* **Python:** Test automation programming.
* **pytest:** Test execution and assertions.
* **Requests:** HTTP API testing.
* **Selenium:** Browser automation.
* **pytest-html:** HTML test reporting.
* **Git and GitHub:** Version control and project collaboration.

## Project Structure

```text
software-testing-project/
├── api_tests/
│   ├── test_results_api.py
│   ├── test_school_fees.py
│   ├── test_students_api.py
│   └── test_users_api.py
├── pages/
│   └── login_page.py
├── Test/
│   ├── test_calculator.py
│   ├── test_google.py
│   └── test_login.py
├── reports/
├── .vscode/
├── .gitignore
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Prerequisites

* Python installed on your computer.
* Git installed.
* Visual Studio Code (recommended).
* An internet connection for tests that call external APIs or open websites.

## Installation

Clone the repository after it has been published to GitHub:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd software-testing-project
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

## Running the Tests

Run the complete test suite:

```powershell
pytest -v
```

Run API tests only:

```powershell
pytest api_tests -v
```

Run browser and other tests:

```powershell
pytest Test -v
```

Generate an HTML report:

```powershell
pytest -v --html=reports/full_test_report.html --self-contained-html
```

Open the generated report in your browser to review test results.

## Current Test Coverage

* Student record retrieval and response validation.
* Examination result retrieval and sample score-to-grade rules.
* School-fee amount and payment-status validation.
* Duplicate-payment detection logic.
* API requests, updates, deletion, error responses, and data-type checks.
* Browser-based login success and failure scenarios.

## Current Limitations

This is a work in progress.

* Some API tests use JSONPlaceholder, a public demonstration API.
* Some school-fee and grading tests validate local test logic rather than a live school application.
* A persistent school database has not yet been integrated.
* A real payment-provider sandbox has not yet been integrated.
* Teacher-salary payment testing is planned for a future stage.
* Sample grading rules are illustrative and must be adapted to the relevant institution's official policy.

No real student records, employee payroll data, payment credentials, or live-money transactions should be used in demonstration tests.

## Planned Improvements

1. Build a student-results API with persistent database storage.
2. Add database-backed school-fee payment tests.
3. Build teacher-salary and payroll validation tests.
4. Integrate a payment-provider sandbox using protected environment variables.
5. Add automated test reporting and continuous integration with GitHub Actions.
6. Expand positive, negative, boundary, security, and regression test coverage.

## Author

**Amabo Ghislain**

Software Testing | QA Automation | Educational Systems

This project demonstrates ongoing practical learning in software quality assurance and test automation.
