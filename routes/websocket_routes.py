import logging
import utils.logger
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool
from utils.websocket_manager import manager
from utils.ws_auth import authorize_ws_user
from students_module.students_models import StudentModel
from teachers_module.services.teacher_services import TeacherService

router=APIRouter(tags=["WebSockets"])

MAX_MESSAGE_LENGTH=2000

# @router.websocket("/ws/fyp_chat/{fyp_id}/{user_type}/{user_id}")
# async def websocket_chat_endpoint(websocket:WebSocket,fyp_id:int,user_type:str,user_id:int):
#     room_id=f"fyp_{fyp_id}"
#     await manager.connect(websocket,room_id)
#     try:
#         while True:
#             client_message=await websocket.receive_text()
#             if user_type=="student":
#                 StudentModel.insert_fyp_message(fyp_id,user_id,'student',client_message.strip())
#             if user_type=="teacher":
#                 TeacherService.send_fyp_message(user_id,fyp_id,client_message.strip())

#             message_payload={
#                 "sender_id":user_id,
#                 "sender_type":user_type,
#                 "message":client_message
#             }    
#             await manager.broadcast_to_room(room_id,message_payload)
#     except WebSocketDisconnect as wd:
#         logging.exception(f"During websct routes api: {str(wd)}")
#         manager.disconnect(websocket,room_id)
                



@router.websocket("/ws/fyp_chat/{fyp_id}/{user_type}/{user_id}")
async def websocket_chat_endpoint(websocket:WebSocket,fyp_id:int,user_type:str,user_id:int):
    user=await run_in_threadpool(authorize_ws_user,websocket,fyp_id,user_type,user_id)
    if not user:
        await websocket.close(code=1008)
        return

    room_id=f"fyp_{fyp_id}"
    await manager.connect(websocket,room_id)
    try:
        while True:
            client_message=(await websocket.receive_text()).strip()
            if not client_message or len(client_message) > MAX_MESSAGE_LENGTH:
                continue

            try:
                if user["role"]=="student":
                    await run_in_threadpool(StudentModel.insert_fyp_message,fyp_id,user["id"],"student",client_message)
                else:
                    await run_in_threadpool(TeacherService.send_fyp_message,user["id"],fyp_id,client_message)
            except Exception as e:
                logging.exception(f"Websocket save message failed: {str(e)}")
                continue  

            message_payload={
                "sender_id":user["id"],
                "sender_type":user["role"],
                "message":client_message,
            }
            await manager.broadcast_to_room(room_id,message_payload)

    except WebSocketDisconnect:
        logging.info(f"FYP chat disconnected: {room_id}")
    except Exception as e:
        logging.exception(f"During websocket routes api: {str(e)}")
    finally:
        manager.disconnect(websocket,room_id)