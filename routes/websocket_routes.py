from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from utils.websocket_manager import manager
from students_module.students_models import StudentModel
from teachers_module.services.teacher_services import TeacherService
import logging
import utils.logger 

router=APIRouter(tags=["WebSockets"])

@router.websocket("/ws/fyp_chat/{fyp_id}/{user_type}/{user_id}")
async def websocket_chat_endpoint(websocket:WebSocket,fyp_id:int,user_type:str,user_id:int):
    room_id=f"fyp_{fyp_id}"
    await manager.connect(websocket,room_id)
    try:
        while True:
            client_message=await websocket.receive_text()
            if user_type=="student":
                StudentModel.insert_fyp_message(fyp_id,user_id,'student',client_message.strip())
            if user_type=="teacher":
                TeacherService.send_fyp_message(user_id,fyp_id,client_message.strip())

            message_payload={
                "sender_id":user_id,
                "sender_type":user_type,
                "message":client_message
            }    
            await manager.broadcast_to_room(room_id,message_payload)
    except WebSocketDisconnect as wd:
        logging.exception(f"During websct routes api: {str(wd)}")
        manager.disconnect(websocket,room_id)
                
