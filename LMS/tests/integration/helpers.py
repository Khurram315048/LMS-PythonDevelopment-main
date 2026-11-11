from core.security import create_access_token


ROLE_DATA = {
    "student": ("student_id", 201, "/student_login"),
    "teacher": ("teacher_id", 301, "/teacher_login"),
    "admin": ("admin_id", 401, "/admin_login"),
}


def make_token(role):
    claim_name, role_id, _login_path = ROLE_DATA[role]
    return create_access_token({
        "user_id": 100,
        "role": role,
        claim_name: role_id,
    })