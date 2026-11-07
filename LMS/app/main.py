import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from core.config import SECRET_KEY, BASE_DIR
from core import logger  
from modules.auth.routes import router as auth_router
from modules.notifications.websocket_routes import router as websocket_router
from modules.students.routes import router as student_router
from modules.teachers.routes import router as teacher_router
from modules.admin.routes import router as admin_router
from modules.chatbot.routes import router as chat_router
from modules.files.routes import router as files_router

app=FastAPI()
app.add_middleware(SessionMiddleware,secret_key=SECRET_KEY,max_age=3600)
app.mount("/static",StaticFiles(directory=str(BASE_DIR / "web" / "static")),name="static")

# app.mount("/uploads",StaticFiles(directory=str(BASE_DIR / "storage" / "students_uploads")),name="uploads")

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(admin_router)
app.include_router(websocket_router)
app.include_router(chat_router)
app.include_router(files_router)


if __name__ == '__main__':
    uvicorn.run("app.main:app",host="127.0.0.1",port=50001,reload=True)