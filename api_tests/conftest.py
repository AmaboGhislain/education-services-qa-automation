from datetime import timedelta
from unittest.mock import Mock

import pytest
import requests


def make_response(status_code, payload=None):
    response = Mock()
    response.status_code = status_code
    response.headers = {"Content-Type": "application/json"}
    response.elapsed = timedelta(milliseconds=5)
    response.json.return_value = payload or {}
    return response


@pytest.fixture(autouse=True)
def mock_jsonplaceholder(monkeypatch):
    def fake_get(url, *args, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is not None and timeout <= 0.000001:
            raise requests.exceptions.Timeout("Simulated timeout")

        if url.endswith("/users/9999") or url.endswith("/posts/9999"):
            return make_response(404)

        if "/posts/" in url:
            return make_response(
                200,
                {
                    "userId": 1,
                    "id": 1,
                    "title": "Sample examination result",
                    "body": "Sample result details",
                },
            )

        if "/users/" in url:
            user_id = int(url.rstrip("/").rsplit("/", 1)[-1])
            user = {
                "id": user_id,
                "name": "Leanne Graham" if user_id == 1 else f"User {user_id}",
                "username": "Bret" if user_id == 1 else f"user{user_id}",
                "email": (
                    "Sincere@april.biz"
                    if user_id == 1
                    else f"user{user_id}@example.com"
                ),
                "address": {
                    "city": "Gwenborough" if user_id == 1 else "Test City"
                },
            }
            return make_response(200, user)

        return make_response(404)

    def fake_post(url, *args, **kwargs):
        payload = kwargs.get("json", {})
        return make_response(201, {**payload, "id": 11})

    def fake_put(url, *args, **kwargs):
        payload = kwargs.get("json", {})
        user_id = int(url.rstrip("/").rsplit("/", 1)[-1])
        return make_response(200, {**payload, "id": user_id})

    def fake_patch(url, *args, **kwargs):
        payload = kwargs.get("json", {})
        user_id = int(url.rstrip("/").rsplit("/", 1)[-1])
        return make_response(200, {**payload, "id": user_id})

    def fake_delete(url, *args, **kwargs):
        return make_response(200)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "put", fake_put)
    monkeypatch.setattr(requests, "patch", fake_patch)
    monkeypatch.setattr(requests, "delete", fake_delete)