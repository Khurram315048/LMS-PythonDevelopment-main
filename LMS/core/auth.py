# from fastapi import Request,HTTPException,status
# from jose import jwt 
# from core.config import SECRET_KEY
# from core.logger import logging
# ALGORITHM="HS256"

# def get_current_user(request:Request)->dict:
#     user_id=request.session.get('user_id')
#     if not user_id:
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
#                             headers={"location": "/main_view"})

#     return {"user_id":user_id}


# def get_current_student(request:Request)->dict:
#     token=request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/student_login"})

#     try:
#         payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
#         if payload.get("role") != "student":
#             raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/student_login"})

#         return payload
#     except jwt.ExpiredSignatureError as ese:
#         logging.exception(f"JWT Token expiration: {str(ese)}")
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/refresh"})
#     except jwt.JWTError as je:
#         logging.exception(f"JWT Token : {str(je)}")
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/student_login"})




# def get_current_teacher(request:Request)->dict:
#     token=request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/teacher_login"})
    
#     try:
#         payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
#         if payload.get("role") != "teacher":
#             raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/teacher_login"})
    
#         return payload
#     except jwt.ExpiredSignatureError as ese:
#         logging.exception(f"JWT Token expiration: {str(ese)}")
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/refresh"})
#     except jwt.JWTError as je:
#         logging.exception(f"JWT Token : {str(je)}")
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/teacher_login"})
    




# def get_current_admin(request:Request)->dict:
#     token=request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/admin_login"})
    
#     try:
#         payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
#         if payload.get("role") != "admin":
#             raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/admin_login"})
    
#         return payload
#     except jwt.ExpiredSignatureError as ese:
#         logging.exception(f"JWT Token expiration: {str(ese)}")
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/refresh"})
#     except jwt.JWTError as je:
#         logging.exception(f"JWT Token : {str(je)}")
#         raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,headers={"location":"/admin_login"})



# def get_chat_user(request:Request)->dict:
#     token=request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="login_required")
#     try:
#         payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="expired")
#     except jwt.JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid")
#     if payload.get("role") not in ("student","teacher","admin"):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="forbidden")
#     return payload







from urllib.parse import quote

from fastapi import HTTPException, Request, status

from core.logger import logging
from core.security import (ACCESS, ALGORITHM, TokenExpired, TokenInvalid,  # noqa: F401
                           decode_token)

LOGIN_URL = {
    "student": "/student_login",
    "teacher": "/teacher_login",
    "admin": "/admin_login",
}


def get_current_user(request: Request) -> dict:
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                            headers={"location": "/main_view"})
    return {"user_id": user_id}


def _redirect(url: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"location": url})


def _refresh_url(request: Request) -> str:
    # GET page par wapas usi page par aane ke liye; POST par seedha /refresh
    if request.method == "GET":
        target = request.url.path + (f"?{request.url.query}" if request.url.query else "")
        return f"/refresh?next={quote(target, safe='')}"
    return "/refresh"


def _current(request: Request, role: str) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise _redirect(LOGIN_URL[role])
    try:
        return decode_token(token, ACCESS, expected_role=role)
    except TokenExpired:
        raise _redirect(_refresh_url(request))
    except TokenInvalid as e:
        logging.warning(f"Rejected access token for {role} page: {e}")
        raise _redirect(LOGIN_URL[role])


def get_current_student(request: Request) -> dict:
    return _current(request, "student")


def get_current_teacher(request: Request) -> dict:
    return _current(request, "teacher")


def get_current_admin(request: Request) -> dict:
    return _current(request, "admin")


def get_chat_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="login_required")
    try:
        return decode_token(token, ACCESS)          # student / teacher / admin, teeno theek
    except TokenExpired:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="expired")
    except TokenInvalid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid")