import pytest
from fastapi import HTTPException
from starlette.requests import Request

from core.auth import get_current_admin, get_current_student, get_current_teacher
from core.security import create_access_token


def make_request(cookie_value=None):
    headers = []
    if cookie_value:
        headers.append((b"cookie", f"access_token={cookie_value}".encode()))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/test",
        "raw_path": b"/test",
        "query_string": b"",
        "headers": headers,
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
    }
    return Request(scope)


def test_student_dependency_rejects_missing_token():
    with pytest.raises(HTTPException) as exc:
        get_current_student(make_request())

    assert exc.value.status_code == 303
    assert exc.value.headers["location"] == "/student_login"


def test_student_dependency_accepts_student_token():
    token = create_access_token({
        "user_id": 10,
        "role": "student",
        "student_id": 20,
    })

    user = get_current_student(make_request(token))

    assert user["user_id"] == 10
    assert user["role"] == "student"
    assert user["student_id"] == 20


def test_admin_dependency_rejects_student_token():
    token = create_access_token({
        "user_id": 10,
        "role": "student",
        "student_id": 20,
    })

    with pytest.raises(HTTPException) as exc:
        get_current_admin(make_request(token))

    assert exc.value.status_code == 303
    assert exc.value.headers["location"] == "/admin_login"


def test_teacher_dependency_rejects_student_token():
    token = create_access_token({
        "user_id": 10,
        "role": "student",
        "student_id": 20,
    })

    with pytest.raises(HTTPException) as exc:
        get_current_teacher(make_request(token))

    assert exc.value.status_code == 303
    assert exc.value.headers["location"] == "/teacher_login"