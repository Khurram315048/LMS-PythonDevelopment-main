import logging

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import RedirectResponse

from core.cookies import REFRESH_COOKIE, clear_auth_cookies, set_auth_cookies
from core.security import (REFRESH, ROLE_ID_CLAIM, TokenError, create_access_token,
                           create_refresh_token, decode_token)

router = APIRouter()

DASHBOARD_URL = {
    "student": "/student_dashboard",
    "teacher": "/teacher_dashboard",
    "admin": "/admin_dashboard",
}


def _safe_next(value: str | None, role: str) -> str:
    # sirf apni site ka relative path; open redirect aur /refresh loop se bachav
    if (value and value.startswith("/") and not value.startswith("//")
            and "\\" not in value and not value.startswith("/refresh")):
        return value
    return DASHBOARD_URL[role]


@router.get("/refresh")
def refresh_session(request: Request, next_url: str | None = Query(None, alias="next")):
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        request.session["flash_error"] = "Session expired. Please login again."
        return RedirectResponse(url="/main_view", status_code=status.HTTP_303_SEE_OTHER)

    try:
        claims = decode_token(token, REFRESH)     # type, signature, exp, role, claims
    except TokenError as e:
        logging.warning(f"Refresh rejected: {e}")
        response = RedirectResponse(url="/main_view", status_code=status.HTTP_303_SEE_OTHER)
        clear_auth_cookies(response)
        return response

    role = claims["role"]
    id_claim = ROLE_ID_CLAIM[role]
    payload = {"user_id": claims["user_id"], "role": role, id_claim: claims[id_claim]}

    response = RedirectResponse(url=_safe_next(next_url, role),
                                status_code=status.HTTP_303_SEE_OTHER)
    set_auth_cookies(response, create_access_token(payload), create_refresh_token(payload))
    return response