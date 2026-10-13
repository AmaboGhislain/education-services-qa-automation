
import requests


def test_get_student_record():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/1",
        timeout=10
    )

    assert response.status_code == 200

    student = response.json()

    assert student["id"] == 1
    assert student["name"] == "Leanne Graham"
    assert "email" in student
    assert "address" in student
    assert "city" in student["address"]


def test_get_nonexistent_student():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/9999",
        timeout=10
    )

    assert response.status_code == 404


def test_student_record_data_validation():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/1",
        timeout=10
    )

    assert response.status_code == 200

    student = response.json()

    assert isinstance(student["id"], int)
    assert isinstance(student["name"], str)
    assert student["name"].strip() != ""

    assert isinstance(student["email"], str)
    assert student["email"].strip() != ""

    assert isinstance(student["address"], dict)
    assert isinstance(student["address"]["city"], str)
    assert student["address"]["city"].strip() != ""