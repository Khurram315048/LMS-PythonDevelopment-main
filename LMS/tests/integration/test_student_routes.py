import pytest

from tests.integration.helpers import ROLE_DATA, make_token


STUDENT_PAGES = [
    "/student_dashboard",
    "/student_profile",
    "/student_fee",
    "/notifications",
    "/student_fyp",
    "/my_submissions",
]


@pytest.mark.parametrize("path", STUDENT_PAGES)
def test_student_pages_reject_no_token(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == ROLE_DATA["student"][2]


@pytest.mark.parametrize("path", STUDENT_PAGES)
@pytest.mark.parametrize("wrong_role", ["teacher", "admin"])
def test_student_pages_reject_other_roles(client, path, wrong_role):
    client.cookies.set("access_token", make_token(wrong_role))
    try:
        response = client.get(path, follow_redirects=False)
    finally:
        client.cookies.clear()

    assert response.status_code == 303
    assert response.headers["location"] == ROLE_DATA["student"][2]