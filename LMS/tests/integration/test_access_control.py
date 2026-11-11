import pytest

from core.security import create_access_token


@pytest.mark.parametrize(
    ("path", "role", "role_claim", "role_id", "login_path"),
    [
        (
            "/student_dashboard",
            "student",
            "student_id",
            20,
            "/student_login",
        ),
        (
            "/teacher_dashboard",
            "teacher",
            "teacher_id",
            30,
            "/teacher_login",
        ),
        (
            "/admin_dashboard",
            "admin",
            "admin_id",
            40,
            "/admin_login",
        ),
    ],
)
def test_protected_route_redirects_without_login(
    client, path, role, role_claim, role_id, login_path
):
    response = client.get(path, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == login_path


def test_admin_route_rejects_student_token(client):
    token = create_access_token({
        "user_id": 10,
        "role": "student",
        "student_id": 20,
    })

    response = client.get(
        "/admin_dashboard",
        cookies={"access_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/admin_login"