import logging
from urllib.parse import urlparse
from fastapi import WebSocket
from jose import jwt, JWTError
from config import SECRET_KEY
from utils.auth import ALGORITHM
from utils.db import mysql
from students_module.services.student_services import StudentService


def _origin_ok(websocket: WebSocket)->bool:
    origin=websocket.headers.get("origin")
    if not origin:
        
        return True
    return urlparse(origin).netloc==websocket.headers.get("host")


def authorize_ws_user(websocket:WebSocket,fyp_id:int,url_user_type:str,url_user_id:int):
    if not _origin_ok(websocket):
        return None

    token=websocket.cookies.get("access_token")
    if not token:
        return None

    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except JWTError:
        return None

    role=payload.get("role")
    if role not in ("student","teacher") or role != url_user_type:
        return None

    real_id=payload.get(f"{role}_id")
    if real_id is None or int(real_id) != url_user_id:
        return None
    real_id=int(real_id)

    try:
        if role=="student":
            StudentService.check_fyp_semester(real_id)      
            if StudentService.check_freeze_student(real_id):  
                return None
            
            owner_col="student_id"
        else:
            owner_col="teacher_id"

        conn=mysql.get_dict_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT 1 FROM fyp_groups WHERE fyp_id=%s AND {owner_col}=%s AND teacher_id IS NOT NULL",(fyp_id, real_id),)
                if not cursor.fetchone():
                    return None
        finally:
            conn.close()
    except Exception as e:
        logging.warning(f"wbsck auth rjctd: {str(e)}")
        return None

    return {
        "role":role,
        "id":real_id
        }