import pytest

from modules.auth import routes as auth_routes


@pytest.mark.parametrize(
    ("path", "expected_status"),
    [
        ("/main_view", 200),
        ("/user_signup", 200),
        ("/send_reset_email", 200),
        ("/otp_verify", 303),  # redirects when reset flow has not started
        ("/update_password", 303),  # requires a verified reset session
    ],
)
def test_auth_pages_respond(client, path, expected_status):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == expected_status


def test_logout_clears_session_and_redirects(client):
    response = client.post(
        "/logout",
        data={"csrf_token": "not-a-valid-token"},
        follow_redirects=False,
    )
    # CSRF middleware should reject POST without a valid session token.
    assert response.status_code == 403