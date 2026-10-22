from jose import jwt ,JWTError
from datetime import datetime,timezone,timedelta
from config import SECRET_KEY
ALGORITHM="HS256"

def create_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=30)
    to_encode.update({
        "exp":expire
    })
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token


def verify_token(token:str):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None



def refresh_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(days=7)
    to_encode.update({
        "exp":expire
    })
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)