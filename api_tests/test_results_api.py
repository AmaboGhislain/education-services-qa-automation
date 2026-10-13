
import requests


def test_get_examination_result():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/posts/1",
        timeout=10
    )

    assert response.status_code == 200

    result = response.json()

    assert result["userId"] == 1
    assert result["id"] == 1
    assert isinstance(result["title"], str)
    assert result["title"].strip() != ""
    assert isinstance(result["body"], str)
    assert result["body"].strip() != ""


def test_nonexistent_examination_result():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/posts/9999",
        timeout=10
    )

    assert response.status_code == 404


import pytest


@pytest.mark.parametrize(
    "score, expected_valid",
    [
        (0, True),
        (50, True),
        (100, True),
        (-1, False),
        (101, False),
    ]
)
def test_examination_score_validation(score, expected_valid):
    is_valid = 0 <= score <= 100

    assert is_valid == expected_valid


def calculate_grade(score):
    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100")

    if score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


@pytest.mark.parametrize(
    "score, expected_grade",
    [
        (100, "A"),
        (80, "A"),
        (79, "B"),
        (70, "B"),
        (69, "C"),
        (60, "C"),
        (59, "D"),
        (50, "D"),
        (49, "F"),
        (0, "F"),
    ]
)
def test_calculate_grade(score, expected_grade):
    assert calculate_grade(score) == expected_grade