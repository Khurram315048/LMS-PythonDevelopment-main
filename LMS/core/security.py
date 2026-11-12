# from jose import jwt ,JWTError
# from datetime import datetime,timezone,timedelta
# from core.config import SECRET_KEY
# ALGORITHM="HS256"

# def create_token(data:dict):
#     to_encode=data.copy()
#     expire=datetime.now(timezone.utc)+timedelta(minutes=30)
#     to_encode.update({
#         "exp":expire
#     })
#     token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
#     return token


# def verify_token(token:str):
#     try:
#         payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
#         return payload
#     except JWTError:
#         return None



# def refresh_token(data:dict):
#     to_encode=data.copy()
#     expire=datetime.now(timezone.utc)+timedelta(days=7)
#     to_encode.update({
#         "exp":expire
#     })
#     return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)





import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from core.config import SECRET_KEY,ACCESS_TOKEN_MINUTES,REFRESH_TOKEN_DAYS

ALGORITHM="HS256"
ISSUER="lms"

ACCESS="access"
REFRESH="refresh"


ROLE_ID_CLAIM={
    "student":"student_id",
    "teacher":"teacher_id",
    "admin":"admin_id",
}


class TokenError(Exception):
    """Token  not acceptable."""


class TokenExpired(TokenError):
    """Signature is right but token expire."""


class TokenInvalid(TokenError):
    """Signature, type, role nothing wrong in these."""


def _signing_key(token_type:str) -> str:
    return hmac.new(SECRET_KEY.encode(), f"lms-jwt:{token_type}".encode(),
                    hashlib.sha256).hexdigest()


def _create(data:dict,token_type:str,lifetime: timedelta) -> str:
    role=data.get("role")
    id_claim=ROLE_ID_CLAIM.get(role)
    if not id_claim or data.get("user_id") is None or data.get(id_claim) is None:
        raise ValueError(f"token needs user_id, role and {id_claim or 'a role id'}")

    now=datetime.now(timezone.utc)
    claims={                       
        "iss":ISSUER,
        "type":token_type,
        "role":role,
        "user_id":data["user_id"],
        id_claim:data[id_claim],
        "iat":now,
        "exp":now + lifetime,
        "jti":uuid.uuid4().hex,
    }
    return jwt.encode(claims, _signing_key(token_type),algorithm=ALGORITHM)


def create_access_token(data:dict) -> str:
    return _create(data,ACCESS,timedelta(minutes=ACCESS_TOKEN_MINUTES))


def create_refresh_token(data:dict) -> str:
    return _create(data,REFRESH,timedelta(days=REFRESH_TOKEN_DAYS))


def decode_token(token:str,expected_type:str,expected_role:str | None = None) -> dict:
    """Signature, expiry, issuer, type, role or required claims are check here."""
    try:
        payload=jwt.decode(token, _signing_key(expected_type),algorithms=[ALGORITHM],issuer=ISSUER)
    except ExpiredSignatureError as e:
        raise TokenExpired("token expired") from e
    except JWTError as e:
        raise TokenInvalid(f"bad token: {e}") from e

    if payload.get("type") != expected_type:
        raise TokenInvalid("wrong token type")

    role=payload.get("role")
    id_claim=ROLE_ID_CLAIM.get(role)
    if not id_claim:
        raise TokenInvalid("unknown role")
    if expected_role and role != expected_role:
        raise TokenInvalid("wrong role")

    for claim in ("user_id",id_claim,"jti"):
        if payload.get(claim) in (None, ""):
            raise TokenInvalid(f"missing claim: {claim}")
    return payload



create_token=create_access_token
refresh_token=create_refresh_token
