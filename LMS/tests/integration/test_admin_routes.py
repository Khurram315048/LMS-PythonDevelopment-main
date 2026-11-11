import pytest

from tests.integration.helpers import ROLE_DATA, make_token


ADMIN_PAGES = [
    "/admin_dashboard",
    "/admin_profile",
    "/system_settings",
    "/complaints",
    "/register_student",
    "/course_registration",
    "/fee_management",
    "/fyp_proposals",
    "/exam_dates",
    "/promote_students",
]


@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_admin_pages_reject_no_token(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == ROLE_DATA["admin"][2]


@pytest.mark.parametrize("path", ADMIN_PAGES)
@pytest.mark.parametrize("wrong_role", ["student", "teacher"])
def test_admin_pages_reject_other_roles(client, path, wrong_role):
    client.cookies.set("access_token", make_token(wrong_role))
    try:
        response = client.get(path, follow_redirects=False)
    finally:
        client.cookies.clear()

    assert response.status_code == 303
    assert response.headers["location"] == ROLE_DATA["admin"][2]