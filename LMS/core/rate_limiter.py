import logging
import math
import threading
import time
import redis
from fastapi import Request
from core.config import REDIS_URL
from core.exceptions import BusinessRuleError, NotFoundError

LOGIN_MAX_FAILS=5            
LOGIN_WINDOW=15 * 60         
LOGIN_IP_MAX_FAILS=20        
OTP_PER_EMAIL=3              
OTP_EMAIL_WINDOW=15 * 60
OTP_PER_IP=10                
OTP_IP_WINDOW=60 * 60
OTP_COOLDOWN=60              

_r=redis.Redis.from_url(REDIS_URL,decode_responses=True,socket_connect_timeout=1,socket_timeout=1)


_mem: dict={}
_lock = threading.Lock()


class TooManyAttempts(Exception):
    def __init__(self, retry_after: int):
        self.retry_after=max(int(retry_after), 1)
        super().__init__(f"Too many attempts. Retry in {self.retry_after}s")

    @property
    def minutes(self) -> int:
        return max(math.ceil(self.retry_after / 60), 1)


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"



def _mem_peek(key):
    now=time.time()
    with _lock:
        count, exp=_mem.get(key,(0,0))
        if exp <= now:
            _mem.pop(key,None)
            return 0, 0
        return count, int(exp - now)


def _mem_incr(key, window):
    now=time.time()
    with _lock:
        count, exp=_mem.get(key, (0, 0))
        if exp <= now:
            count, exp=0, now + window
        count += 1
        _mem[key]=(count, exp)
        return count,int(exp - now)


def _incr(key:str,window:int):
    try:
        pipe=_r.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        count, ttl=pipe.execute()
        if ttl < 0:                      
            _r.expire(key, window)
            ttl=window
        return count, ttl
    except redis.RedisError:
        logging.exception("rate limiter: redis unavailable, using memory")
        return _mem_incr(key, window)


def _peek(key: str):
    try:
        pipe= _r.pipeline()
        pipe.get(key)
        pipe.ttl(key)
        value, ttl=pipe.execute()
        return int(value or 0), max(ttl, 0)
    except redis.RedisError:
        logging.exception("rate limiter: redis unavailable, using memory")
        return _mem_peek(key)


def _reset(key:str):
    try:
        _r.delete(key)
    except redis.RedisError:
        logging.exception("rate limiter: redis unavailable, using memory")
    with _lock:
        _mem.pop(key, None)



def _login_keys(role:str,email:str,ip:str):
    return (f"lf:{role}:{(email or '').strip().lower()}",LOGIN_MAX_FAILS), \
           (f"lf_ip:{ip}",LOGIN_IP_MAX_FAILS)


def check_login_allowed(role:str,email:str,ip:str):
    for key, limit in _login_keys(role,email,ip):
        count, ttl= _peek(key)
        if count >= limit:
            raise TooManyAttempts(ttl or LOGIN_WINDOW)


def record_login_failure(role:str,email:str,ip:str):
    for key, _ in _login_keys(role,email,ip):
        _incr(key,LOGIN_WINDOW)


def clear_login_failures(role:str,email:str):
    _reset(_login_keys(role,email,"")[0][0])


def guarded_authenticate(role:str,email:str,password:str,ip:str,authenticate):
    check_login_allowed(role,email,ip)
    try:
        result=authenticate(email,password)
    except (BusinessRuleError, NotFoundError):
        record_login_failure(role,email,ip)
        raise
    clear_login_failures(role,email)
    return result



def check_otp_send(email:str,ip:str):
    email=(email or "").strip().lower()

    _, cd_ttl=_peek(f"otp_cd:{email}")
    if cd_ttl:
        raise TooManyAttempts(cd_ttl)

    count, ttl=_incr(f"otp_email:{email}",OTP_EMAIL_WINDOW)
    if count > OTP_PER_EMAIL:
        raise TooManyAttempts(ttl)

    count, ttl=_incr(f"otp_ip:{ip}",OTP_IP_WINDOW)
    if count > OTP_PER_IP:
        raise TooManyAttempts(ttl)

    _incr(f"otp_cd:{email}",OTP_COOLDOWN)