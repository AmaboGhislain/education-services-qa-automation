
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


def create_test_student(client):
    return client.post(
        "/students",
        json={
            "student_number": "PAY-TEST-001",
            "full_name": "Payment Test Student",
            "class_name": "Form 5",
        },
    )


def test_create_payment(client):
    student_response = create_test_student(client)

    assert student_response.status_code == 201
    student_id = student_response.json()["id"]

    payment_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-TEST-1001",
            "student_id": student_id,
            "amount": 75000,
            "currency": "XAF",
            
        },
    )

    assert payment_response.status_code == 201

    payment = payment_response.json()
    assert payment["payment_reference"] == "PAY-TEST-1001"
    assert payment["student_id"] == student_id
    assert payment["amount"] == 75000
    assert payment["currency"] == "XAF"
    assert payment["status"] == "PENDING"
    assert "id" in payment
    assert "created_at" in payment


@pytest.mark.parametrize("amount", [0, -5000])
def test_reject_invalid_payment_amount(client, amount):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    payment_response = client.post(
        "/payments",
        json={
            "payment_reference": f"INVALID-{abs(amount)}",
            "student_id": student_id,
            "amount": amount,
            "currency": "XAF",
            
        },
    )

    assert payment_response.status_code == 422


def test_reject_invalid_payment_currency(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    payment_response = client.post(
        "/payments",
        json={
            "payment_reference": "INVALID-CURRENCY-001",
            "student_id": student_id,
            "amount": 75000,
            "currency": "USD",
            
        },
    )

    assert payment_response.status_code == 422


def test_reject_payment_for_nonexistent_student(client):
    payment_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-NO-STUDENT-001",
            "student_id": 99999,
            "amount": 75000,
            "currency": "XAF",
            
        },
    )

    assert payment_response.status_code == 404
    assert payment_response.json()["detail"] == "Student not found"


def test_reject_duplicate_payment_reference(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    payment_data = {
        "payment_reference": "PAY-DUPLICATE-001",
        "student_id": student_id,
        "amount": 75000,
        "currency": "XAF",
        
    }

    first_response = client.post("/payments", json=payment_data)
    second_response = client.post("/payments", json=payment_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Payment reference already exists"


def test_get_payment_by_id(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    create_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-RETRIEVE-001",
            "student_id": student_id,
            "amount": 50000,
            "currency": "XAF",
            
        },
    )

    assert create_response.status_code == 201
    payment_id = create_response.json()["id"]

    get_response = client.get(f"/payments/{payment_id}")

    assert get_response.status_code == 200
    payment = get_response.json()
    assert payment["id"] == payment_id
    assert payment["payment_reference"] == "PAY-RETRIEVE-001"
    assert payment["amount"] == 50000
    assert payment["student_id"] == student_id


def test_get_student_payments(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    first_payment = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-STUDENT-001",
            "student_id": student_id,
            "amount": 50000,
            "currency": "XAF",
            
        },
    )

    second_payment = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-STUDENT-002",
            "student_id": student_id,
            "amount": 25000,
            "currency": "XAF",
            
        },
    )

    assert first_payment.status_code == 201
    assert second_payment.status_code == 201

    response = client.get(f"/students/{student_id}/payments")

    assert response.status_code == 200

    payments = response.json()
    assert len(payments) == 2
    assert payments[0]["payment_reference"] == "PAY-STUDENT-001"
    assert payments[1]["payment_reference"] == "PAY-STUDENT-002"


def test_get_nonexistent_payment(client):
    response = client.get("/payments/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_get_payments_for_nonexistent_student(client):
    response = client.get("/students/99999/payments")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_client_cannot_set_initial_payment_status(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    payment_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-SECURITY-001",
            "student_id": student_id,
            "amount": 75000,
            "currency": "XAF",
            "status": "SUCCESS",
        },
    )

    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "PENDING"


def test_verify_pending_payment_as_successful(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    create_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-VERIFY-SUCCESS-001",
            "student_id": student_id,
            "amount": 75000,
            "currency": "XAF",
        },
    )

    assert create_response.status_code == 201
    payment_id = create_response.json()["id"]
    assert create_response.json()["status"] == "PENDING"

    verify_response = client.post(
    f"/payments/{payment_id}/verify",
    json={"outcome": "SUCCESS"},
    headers={"X-Simulator-Key": "local-test-simulator-key"},
)

    assert verify_response.status_code == 200
    assert verify_response.json()["status"] == "SUCCESS"


def test_verify_pending_payment_as_failed(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    create_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-VERIFY-FAILED-001",
            "student_id": student_id,
            "amount": 50000,
            "currency": "XAF",
        },
    )

    assert create_response.status_code == 201
    payment_id = create_response.json()["id"]
    assert create_response.json()["status"] == "PENDING"

    verify_response = client.post(
        f"/payments/{payment_id}/verify",
        json={"outcome": "FAILED"},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )

    assert verify_response.status_code == 200
    assert verify_response.json()["status"] == "FAILED"


def test_cannot_verify_payment_twice(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    create_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-VERIFY-ONCE-001",
            "student_id": student_id,
            "amount": 60000,
            "currency": "XAF",
        },
    )

    assert create_response.status_code == 201
    payment_id = create_response.json()["id"]

    first_verification = client.post(
        f"/payments/{payment_id}/verify",
        json={"outcome": "SUCCESS"},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )

    assert first_verification.status_code == 200
    assert first_verification.json()["status"] == "SUCCESS"

    second_verification = client.post(
        f"/payments/{payment_id}/verify",
        json={"outcome": "FAILED"},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )

    assert second_verification.status_code == 409
    assert second_verification.json()["detail"] == (
        "Only pending payments can be verified"
    )



@pytest.mark.parametrize(
    "outcome",
    ["UNKNOWN", "PENDING", "", "SUCCESSFUL"],
)
def test_reject_invalid_payment_verification_outcome(client, outcome):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    create_response = client.post(
        "/payments",
        json={
            "payment_reference": f"PAY-INVALID-OUTCOME-{len(outcome)}",
            "student_id": student_id,
            "amount": 40000,
            "currency": "XAF",
        },
    )

    assert create_response.status_code == 201
    payment_id = create_response.json()["id"]

    verify_response = client.post(
        f"/payments/{payment_id}/verify",
        json={"outcome": outcome},
    )

    assert verify_response.status_code == 422


def test_verify_nonexistent_payment(client):
    response = client.post(
        "/payments/99999/verify",
        json={"outcome": "SUCCESS"},
        headers={"X-Simulator-Key": "local-test-simulator-key"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_reject_payment_verification_without_api_key(client):
    create_test_student(client)

    payment_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-NO-KEY-001",
            "student_id": 1,
            "amount": 5000,
            "currency": "XAF",
        },
    )

    assert payment_response.status_code == 201
    payment_id = payment_response.json()["id"]

    response = client.post(
        f"/payments/{payment_id}/verify",
        json={"outcome": "SUCCESS"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or missing simulator API key"
    )

    payment_check = client.get(f"/payments/{payment_id}")
    assert payment_check.status_code == 200
    assert payment_check.json()["status"] == "PENDING"

    
def test_reject_payment_verification_with_wrong_api_key(client):
    create_test_student(client)

    payment_response = client.post(
        "/payments",
        json={
            "payment_reference": "PAY-WRONG-KEY-001",
            "student_id": 1,
            "amount": 5000,
            "currency": "XAF",
        },
    )

    assert payment_response.status_code == 201
    payment_id = payment_response.json()["id"]

    response = client.post(
        f"/payments/{payment_id}/verify",
        json={"outcome": "SUCCESS"},
        headers={"X-Simulator-Key": "wrong-key"},
    )

    assert response.status_code == 401

    payment_check = client.get(f"/payments/{payment_id}")
    assert payment_check.status_code == 200
    assert payment_check.json()["status"] == "PENDING"



