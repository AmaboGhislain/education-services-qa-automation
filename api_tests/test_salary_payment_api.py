import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from education_api.database import Base, get_db
from education_api.main import app


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def create_test_teacher(client):
    return client.post(
        "/teachers",
        json={
            "employee_number": "SAL-TEST-001",
            "full_name": "Salary Test Teacher",
            "department": "Mathematics",
        },
    )


def test_get_salary_payment_by_id(client):
    teacher_response = create_test_teacher(client)
    assert teacher_response.status_code == 201
    teacher_id = teacher_response.json()["id"]

    create_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-TEST-001",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )

    assert create_response.status_code == 201
    salary_payment_id = create_response.json()["id"]

    response = client.get(f"/salary-payments/{salary_payment_id}")

    assert response.status_code == 200
    salary_payment = response.json()
    assert salary_payment["id"] == salary_payment_id
    assert salary_payment["payment_reference"] == "SAL-PAY-TEST-001"
    assert salary_payment["teacher_id"] == teacher_id
    assert salary_payment["amount"] == 250000
    assert salary_payment["payment_month"] == "2026-09"
    assert salary_payment["status"] == "PENDING"


def test_get_nonexistent_salary_payment(client):
    response = client.get("/salary-payments/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Salary payment not found"
def test_create_salary_payment(client):
    teacher_response = create_test_teacher(client)
    assert teacher_response.status_code == 201
    teacher_id = teacher_response.json()["id"]

    response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-CREATE-001",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )

    assert response.status_code == 201
    salary_payment = response.json()
    assert salary_payment["payment_reference"] == "SAL-PAY-CREATE-001"
    assert salary_payment["teacher_id"] == teacher_id
    assert salary_payment["amount"] == 250000
    assert salary_payment["currency"] == "XAF"
    assert salary_payment["payment_month"] == "2026-09"
    assert salary_payment["status"] == "PENDING"
    assert "id" in salary_payment
    assert "created_at" in salary_payment


@pytest.mark.parametrize("amount", [0, -1000])
def test_reject_invalid_salary_payment_amount(client, amount):
    teacher_response = create_test_teacher(client)
    teacher_id = teacher_response.json()["id"]

    response = client.post(
        "/salary-payments",
        json={
            "payment_reference": f"SAL-PAY-INVALID-AMOUNT-{abs(amount)}",
            "teacher_id": teacher_id,
            "amount": amount,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("payment_month", ["2026-13", "2026-00", "Sep-2026"])
def test_reject_invalid_salary_payment_month(client, payment_month):
    teacher_response = create_test_teacher(client)
    teacher_id = teacher_response.json()["id"]

    response = client.post(
        "/salary-payments",
        json={
            "payment_reference": f"SAL-PAY-INVALID-MONTH-{payment_month}",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": payment_month,
        },
    )

    assert response.status_code == 422


def test_reject_salary_payment_for_nonexistent_teacher(client):
    response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-NO-TEACHER-001",
            "teacher_id": 99999,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Teacher not found"

def test_reject_duplicate_salary_payment_reference(client):
    teacher_response = create_test_teacher(client)
    assert teacher_response.status_code == 201
    teacher_id = teacher_response.json()["id"]

    payment_data = {
        "payment_reference": "SAL-PAY-DUPLICATE-001",
        "teacher_id": teacher_id,
        "amount": 250000,
        "currency": "XAF",
        "payment_month": "2026-09",
    }

    first_response = client.post("/salary-payments", json=payment_data)
    second_response = client.post("/salary-payments", json=payment_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Payment reference already exists"

def test_list_teacher_salary_payments(client):
    teacher_response = create_test_teacher(client)
    assert teacher_response.status_code == 201
    teacher_id = teacher_response.json()["id"]

    first_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-LIST-001",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )
    second_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-LIST-002",
            "teacher_id": teacher_id,
            "amount": 260000,
            "currency": "XAF",
            "payment_month": "2026-10",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get(f"/teachers/{teacher_id}/salary-payments")

    assert response.status_code == 200
    payments = response.json()
    assert len(payments) == 2
    assert payments[0]["payment_reference"] == "SAL-PAY-LIST-001"
    assert payments[1]["payment_reference"] == "SAL-PAY-LIST-002"


def test_list_salary_payments_for_nonexistent_teacher(client):
    response = client.get("/teachers/99999/salary-payments")

    assert response.status_code == 404
    assert response.json()["detail"] == "Teacher not found"

def test_list_salary_payments_for_teacher_with_none(client):
    teacher_response = create_test_teacher(client)
    assert teacher_response.status_code == 201
    teacher_id = teacher_response.json()["id"]

    response = client.get(f"/teachers/{teacher_id}/salary-payments")

    assert response.status_code == 200
    assert response.json() == []

def test_verify_salary_payment_as_successful(client):
    teacher_response = create_test_teacher(client)
    assert teacher_response.status_code == 201
    teacher_id = teacher_response.json()["id"]

    create_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-VERIFY-SUCCESS-001",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )
    assert create_response.status_code == 201
    salary_payment_id = create_response.json()["id"]
    assert create_response.json()["status"] == "PENDING"

    response = client.post(
        f"/salary-payments/{salary_payment_id}/verify",
        json={"outcome": "SUCCESS"},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"

def test_verify_salary_payment_as_failed(client):
    teacher_response = create_test_teacher(client)
    assert teacher_response.status_code == 201
    teacher_id = teacher_response.json()["id"]

    create_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-VERIFY-FAILED-001",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )
    assert create_response.status_code == 201
    salary_payment_id = create_response.json()["id"]

    response = client.post(
        f"/salary-payments/{salary_payment_id}/verify",
        json={"outcome": "FAILED"},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"


@pytest.mark.parametrize("outcome", ["UNKNOWN", "PENDING", "", "SUCCESSFUL"])
def test_reject_invalid_salary_payment_verification_outcome(client, outcome):
    teacher_response = create_test_teacher(client)
    teacher_id = teacher_response.json()["id"]

    create_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": f"SAL-PAY-INVALID-OUTCOME-{len(outcome)}",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )
    assert create_response.status_code == 201
    salary_payment_id = create_response.json()["id"]

    response = client.post(
        f"/salary-payments/{salary_payment_id}/verify",
        json={"outcome": outcome},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )

    assert response.status_code == 422


def test_cannot_verify_salary_payment_twice(client):
    teacher_response = create_test_teacher(client)
    teacher_id = teacher_response.json()["id"]

    create_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-VERIFY-TWICE-001",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )
    assert create_response.status_code == 201
    salary_payment_id = create_response.json()["id"]

    first_response = client.post(
        f"/salary-payments/{salary_payment_id}/verify",
        json={"outcome": "SUCCESS"},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/salary-payments/{salary_payment_id}/verify",
        json={"outcome": "FAILED"},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Only pending salary payments can be verified"
    )

def test_reject_salary_payment_verification_without_api_key(client):
    teacher_response = create_test_teacher(client)
    teacher_id = teacher_response.json()["id"]

    create_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-NO-KEY-001",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )
    assert create_response.status_code == 201
    salary_payment_id = create_response.json()["id"]

    response = client.post(
        f"/salary-payments/{salary_payment_id}/verify",
        json={"outcome": "SUCCESS"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing simulator API key"


def test_reject_salary_payment_verification_with_wrong_api_key(client):
    teacher_response = create_test_teacher(client)
    teacher_id = teacher_response.json()["id"]

    create_response = client.post(
        "/salary-payments",
        json={
            "payment_reference": "SAL-PAY-WRONG-KEY-001",
            "teacher_id": teacher_id,
            "amount": 250000,
            "currency": "XAF",
            "payment_month": "2026-09",
        },
    )
    assert create_response.status_code == 201
    salary_payment_id = create_response.json()["id"]

    response = client.post(
        f"/salary-payments/{salary_payment_id}/verify",
        json={"outcome": "SUCCESS"},
        headers={"X-Simulator-Key": "wrong-key"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing simulator API key"