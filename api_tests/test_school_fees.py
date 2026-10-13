
import pytest


def is_valid_payment_amount(amount):
    return isinstance(amount, (int, float)) and not isinstance(amount, bool) and amount > 0


@pytest.mark.parametrize(
    "amount, expected",
    [
        (50000, True),
        (100000, True),
        (0, False),
        (-5000, False),
        (0.01, True),
        (True, False),
    ]
)
def test_payment_amount_validation(amount, expected):
    assert is_valid_payment_amount(amount) == expected


def is_valid_payment_status(status):
    valid_statuses = ["PENDING", "SUCCESS", "FAILED"]
    return status in valid_statuses


@pytest.mark.parametrize(
    "status, expected",
    [
        ("PENDING", True),
        ("SUCCESS", True),
        ("FAILED", True),
        ("UNKNOWN", False),
        ("", False),
        ("success", False),
    ]
)
def test_payment_status_validation(status, expected):
    assert is_valid_payment_status(status) == expected


def test_payment_record_details():
    payment = {
        "payment_id": "PAY-1001",
        "student_id": 25,
        "amount": 75000,
        "currency": "XAF",
        "status": "SUCCESS"
    }

    assert payment["payment_id"] == "PAY-1001"
    assert payment["student_id"] == 25
    assert payment["amount"] == 75000
    assert payment["currency"] == "XAF"
    assert payment["status"] == "SUCCESS"

    assert isinstance(payment["student_id"], int)
    assert isinstance(payment["amount"], (int, float))


def test_failed_payment_status():
    payment = {
        "student_id": 25,
        "amount": 75000,
        "status": "FAILED"
    }

    assert payment["status"] == "FAILED"
    assert payment["status"] != "SUCCESS"


def test_duplicate_payment_detection():
    processed_payment_ids = ["PAY-1001", "PAY-1002"]

    new_payment_id = "PAY-1001"

    assert new_payment_id in processed_payment_ids



def is_duplicate_payment(payment_id, processed_payment_ids):
    return payment_id in processed_payment_ids


def test_detect_duplicate_payment():
    processed_payment_ids = ["PAY-1001", "PAY-1002"]

    assert is_duplicate_payment(
        "PAY-1001",
        processed_payment_ids
    ) is True

    assert is_duplicate_payment(
        "PAY-1003",
        processed_payment_ids
    ) is False