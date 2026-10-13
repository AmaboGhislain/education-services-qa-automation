import requests
import pytest
from unittest.mock import patch



def test_get_user():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/1",
        timeout=10
    )

    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 10
    assert "application/json" in response.headers["Content-Type"]

    data = response.json()

    assert data["id"] == 1
    assert "name" in data
    assert "email" in data

def test_get_nonexistent_user():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/9999"
    )

    assert response.status_code == 404


def test_create_user():
    payload = {
        "name": "Amabo Ghislain",
        "email": "amabo@example.com"
    }

    response = requests.post(
        "https://jsonplaceholder.typicode.com/users",
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Amabo Ghislain"
    assert data["email"] == "amabo@example.com"
    assert "id" in data

def test_update_user():
    payload = {
        "name": "Amabo Ghislain Updated",
        "email": "amabo.updated@example.com"
    }

    response = requests.put(
        "https://jsonplaceholder.typicode.com/users/1",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Amabo Ghislain Updated"
    assert data["email"] == "amabo.updated@example.com"
    assert data["id"] == 1    

def test_partial_update_user():
    payload = {
        "email": "newemail@example.com"
    }

    response = requests.patch(
        "https://jsonplaceholder.typicode.com/users/1",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "newemail@example.com"
    assert data["id"] == 1

def test_delete_user():
    response = requests.delete(
        "https://jsonplaceholder.typicode.com/users/1"
    )

    assert response.status_code == 200

def test_user_response_details():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Leanne Graham"
    assert data["username"] == "Bret"
    assert data["email"] == "Sincere@april.biz"

    assert "application/json" in response.headers["Content-Type"]


def test_api_timeout():
    import requests

    try:
        requests.get(
            "https://jsonplaceholder.typicode.com/users/1",
            timeout=0.000001
        )
        assert False, "Expected a timeout exception"
    except requests.exceptions.Timeout:
        assert True

    
def test_api_server_error():
    with patch(
        "requests.get"
    ) as mock_get:
        mock_get.return_value.status_code = 500

        response = requests.get(
            "https://jsonplaceholder.typicode.com/users/1"
        )

        assert response.status_code == 500


@pytest.mark.parametrize(
    "user_id",
    [1, 2, 3, 4, 5]
)
def test_get_multiple_users(user_id):
    response = requests.get(
        f"https://jsonplaceholder.typicode.com/users/{user_id}",
        timeout=10
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert "name" in data
    assert "email" in data


def test_user_data_types():
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users/1",
        timeout=10
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["username"], str)
    assert isinstance(data["email"], str)
    assert isinstance(data["address"], dict)
    assert isinstance(data["address"]["city"], str)