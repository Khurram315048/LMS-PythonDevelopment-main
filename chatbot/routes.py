import time
import logging
from collections import defaultdict,deque
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel,Field
from utils.auth import get_chat_user
from utils.csrf import verify_csrf
from students_module.services.student_services import StudentService
from chatbot.agent import run_chat,ChatError

router=APIRouter(dependencies=[Depends(verify_csrf)])
_hits=defaultdict(deque)


def _rate_ok(uid:int,limit:int=20,window:int=60)->bool:
    now=time.time()
    q=_hits[uid]
    while q and now-q[0]>window:
        q.popleft()
    if len(q)>=limit:
        return False
    q.append(now)
    return True


class Msg(BaseModel):
    role:Literal["user","assistant"]
    content:str=Field(max_length=800)


class ChatIn(BaseModel):
    message:str=Field(min_length=1,max_length=500)
    history:list[Msg]=Field(default_factory=list,max_length=10)


@router.post("/chat")
def chat(body:ChatIn,user:dict=Depends(get_chat_user)):
    if user["role"] not in("student","teacher"):
        return {
            "reply":"Unauthorized Access"
            }
    
    if not _rate_ok(user["user_id"]):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,detail="Wait to request")
    
    try:
        reply=run_chat(user,body.message,[m.model_dump() for m in body.history])
    except ChatError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=str(e))
    except Exception as e:
        logging.exception(f"Chat route error : {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Try Agin.")
    return {
        "reply":reply
        }