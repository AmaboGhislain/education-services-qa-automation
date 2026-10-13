
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from education_api.database import Base, get_db
from education_api.main import app


@pytest.fixture
def client():
    # Use an isolated in-memory SQLite database for each test.
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


def create_test_student(client, student_number="TEST-001"):
    return client.post(
        "/students",
        json={
            "student_number": student_number,
            "full_name": "Test Student",
            "class_name": "Form 5",
        },
    )


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_student(client):
    response = create_test_student(client)

    assert response.status_code == 201
    assert response.json()["student_number"] == "TEST-001"
    assert response.json()["full_name"] == "Test Student"


def test_duplicate_student_number_is_rejected(client):
    first = create_test_student(client)
    second = create_test_student(client)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "Student number already exists"


def test_create_result(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    response = client.post(
        "/results",
        json={
            "student_id": student_id,
            "subject": "Mathematics",
            "score": 85,
            "term": "First Term",
            "academic_year": "2026-2027",
        },
    )

    assert response.status_code == 201
    assert response.json()["subject"] == "Mathematics"
    assert response.json()["score"] == 85


@pytest.mark.parametrize("invalid_score", [105, -5])
def test_invalid_scores_are_rejected(client, invalid_score):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    response = client.post(
        "/results",
        json={
            "student_id": student_id,
            "subject": "Mathematics",
            "score": invalid_score,
            "term": "First Term",
            "academic_year": "2026-2027",
        },
    )

    assert response.status_code == 422


def test_result_for_missing_student_is_rejected(client):
    response = client.post(
        "/results",
        json={
            "student_id": 999999,
            "subject": "Mathematics",
            "score": 75,
            "term": "First Term",
            "academic_year": "2026-2027",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_retrieve_student_results(client):
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    client.post(
        "/results",
        json={
            "student_id": student_id,
            "subject": "Mathematics",
            "score": 85,
            "term": "First Term",
            "academic_year": "2026-2027",
        },
    )

    response = client.get(f"/students/{student_id}/results")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["subject"] == "Mathematics"
    assert response.json()[0]["score"] == 85