import pytest

from tests.integration.helpers import ROLE_DATA, make_token


TEACHER_PAGES = [
    "/teacher_dashboard",
    "/teacher_profile",
    "/class_attendance",
    "/fyp_management",
]


@pytest.mark.parametrize("path", TEACHER_PAGES)
def test_teacher_pages_reject_no_token(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == ROLE_DATA["teacher"][2]


@pytest.mark.parametrize("path", TEACHER_PAGES)
@pytest.mark.parametrize("wrong_role", ["student", "admin"])
def test_teacher_pages_reject_other_roles(client, path, wrong_role):
    client.cookies.set("access_token", make_token(wrong_role))
    try:
        response = client.get(path, follow_redirects=False)
    finally:
        client.cookies.clear()

    assert response.status_code == 303
    assert response.headers["location"] == ROLE_DATA["teacher"][2]