import secrets
from fastapi import Request,HTTPException,status
import logging


def get_csrf_token(request:Request)->str:
    token=request.session.get("csrf_token")
    if not token:
        token=secrets.token_urlsafe(32)
        request.session["csrf_token"]=token
    return token


async def verify_csrf(request:Request):
    if request.method in ("GET","HEAD","OPTIONS"):
        return

    form=await request.form()
    sent=form.get("csrf_token") or request.headers.get("X-CSRF-TOKEN")
    stored=request.session.get("csrf_token")
    if not stored or not sent or not secrets.compare_digest(str(sent),stored):
        logging.error(f"Error during csrf validation: {request.method} {request.url.path}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="CSRF Token validation failed ")