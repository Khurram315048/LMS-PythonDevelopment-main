from fastapi import Response

from core.config import (ACCESS_TOKEN_MINUTES, COOKIE_SAMESITE, COOKIE_SECURE,
                         REFRESH_TOKEN_DAYS)

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
REFRESH_PATH = "/refresh"        # refresh cookie sirf /refresh par jati hai


def _opts() -> dict:
    return {"httponly": True, "secure": COOKIE_SECURE, "samesite": COOKIE_SAMESITE}


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(ACCESS_COOKIE, access_token, max_age=ACCESS_TOKEN_MINUTES * 60,
                        path="/", **_opts())
    response.set_cookie(REFRESH_COOKIE, refresh_token, max_age=REFRESH_TOKEN_DAYS * 86400,
                        path=REFRESH_PATH, **_opts())
    # purani (path="/") refresh cookie hata dein, warna dono saath jayengi
    response.delete_cookie(REFRESH_COOKIE, path="/")


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/", **_opts())
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_PATH, **_opts())
    response.delete_cookie(REFRESH_COOKIE, path="/")