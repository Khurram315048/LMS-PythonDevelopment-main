# from fastapi import Response

# from core.config import (ACCESS_TOKEN_MINUTES, COOKIE_SAMESITE, COOKIE_SECURE,
#                          REFRESH_TOKEN_DAYS)

# ACCESS_COOKIE="access_token"
# REFRESH_COOKIE="refresh_token"
# REFRESH_PATH="/refresh"        


# def _opts() -> dict:
#     return {
#         "httponly":True,
#         "secure":COOKIE_SECURE,
#         "samesite":COOKIE_SAMESITE
#         }


# def set_auth_cookies(response:Response,access_token:str,refresh_token:str) -> None:
#     response.set_cookie(ACCESS_COOKIE,access_token,max_age=ACCESS_TOKEN_MINUTES * 60,path="/", **_opts())
#     response.set_cookie(REFRESH_COOKIE,refresh_token,max_age=REFRESH_TOKEN_DAYS * 86400,path=REFRESH_PATH, **_opts())
#     response.delete_cookie(REFRESH_COOKIE,path="/")


# def clear_auth_cookies(response: Response) -> None:
#     response.delete_cookie(ACCESS_COOKIE,path="/", **_opts())
#     response.delete_cookie(REFRESH_COOKIE,path=REFRESH_PATH, **_opts())
#     response.delete_cookie(REFRESH_COOKIE,path="/")





from fastapi import Response

from core.config import (ACCESS_TOKEN_MINUTES, COOKIE_SAMESITE, COOKIE_SECURE,
                         REFRESH_TOKEN_DAYS)

ACCESS_COOKIE="access_token"
REFRESH_COOKIE="refresh_token"
REFRESH_PATH="/refresh"
ROLES=("student","teacher","admin")


def access_name(role:str)->str:
    return f"{ACCESS_COOKIE}_{role}"


def refresh_name(role:str)->str:
    return f"{REFRESH_COOKIE}_{role}"


def _opts() -> dict:
    return {
        "httponly":True,
        "secure":COOKIE_SECURE,
        "samesite":COOKIE_SAMESITE
        }


def _clear_legacy(response:Response) -> None:
    # purani single cookies (pehle wala system) saaf karo
    response.delete_cookie(ACCESS_COOKIE,path="/")
    response.delete_cookie(REFRESH_COOKIE,path=REFRESH_PATH)
    response.delete_cookie(REFRESH_COOKIE,path="/")


def set_auth_cookies(response:Response,access_token:str,refresh_token:str,role:str | None=None) -> None:
    if role is None:
        # login routes ko badalna na pade, is liye role token se lete hain
        from core.security import ACCESS, decode_token
        role=decode_token(access_token,ACCESS)["role"]
    response.set_cookie(access_name(role),access_token,max_age=ACCESS_TOKEN_MINUTES * 60,path="/", **_opts())
    response.set_cookie(refresh_name(role),refresh_token,max_age=REFRESH_TOKEN_DAYS * 86400,path=REFRESH_PATH, **_opts())
    _clear_legacy(response)


def clear_auth_cookies(response:Response,role:str | None=None) -> None:
    roles=(role,) if role in ROLES else ROLES      # role na do to teeno saaf
    for r in roles:
        response.delete_cookie(access_name(r),path="/", **_opts())
        response.delete_cookie(refresh_name(r),path=REFRESH_PATH, **_opts())
    _clear_legacy(response)