import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR=Path(__file__).resolve().parent.parent   
load_dotenv(BASE_DIR / ".env")

TEMPLATES_AUTO_RELOAD=True





MYSQL_HOST=os.getenv('MYSQL_HOST','localhost')
MYSQL_USER=os.getenv('MYSQL_USER','root')
MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD','')
MYSQL_DB=os.getenv('MYSQL_DB','lms')
MYSQL_PORT=int(os.getenv('MYSQL_PORT',3306))
SECRET_KEY=os.getenv('SECRET_KEY')
APP_ENV=os.getenv("APP_ENV","development").lower()
COOKIE_SECURE=os.getenv("COOKIE_SECURE","true" if APP_ENV=="production" else "false").lower()=="true"
COOKIE_SAMESITE=os.getenv("COOKIE_SAMESITE","lax").lower()
ACCESS_TOKEN_MINUTES=int(os.getenv("ACCESS_TOKEN_MINUTES","1"))
REFRESH_TOKEN_DAYS=int(os.getenv("REFRESH_TOKEN_DAYS","7"))

if not SECRET_KEY or len(SECRET_KEY)<32:
    raise RuntimeError("SECRET_KEY must be set and at least 32 characters long")
MYSQL_CURSORCLASS='DictCursor'
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
GROQ_MODEL=os.getenv("GROQ_MODEL","llama-3.3-70b-versatile")
CHATBOT_DB_USER=os.getenv("CHATBOT_DB_USER")
CHATBOT_DB_PASSWORD=os.getenv("CHATBOT_DB_PASSWORD")
CHATBOT_SQL_USER=os.getenv("CHATBOT_SQL_USER")
CHATBOT_SQL_PASSWORD=os.getenv("CHATBOT_SQL_PASSWORD")
QDRANT_URL=os.getenv("QDRANT_URL","")
REDIS_URL=os.getenv("REDIS_URL","redis://127.0.0.1:6379/0")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY","")
CHATBOT_TEACHER_DB_USER=os.getenv("CHATBOT_TEACHER_DB_USER")
CHATBOT_TEACHER_DB_PASSWORD=os.getenv("CHATBOT_TEACHER_DB_PASSWORD")

STORAGE_DIR=BASE_DIR / "storage"
UPLOAD_DIR=STORAGE_DIR / "students_uploads"
FEE_UPLOAD_FOLDER=str(UPLOAD_DIR / "voucher_pics")
ASSIGNMENT_UPLOAD_FOLDER=str(UPLOAD_DIR/"students_assignments")
QUIZ_UPLOAD_FOLDER=str(UPLOAD_DIR/"students_quizes")
STUDENT_FYP_FOLDER=str(UPLOAD_DIR/"students_fyp_proposal")
MAIL_USERNAME=os.getenv("MAIL_USERNAME")
MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
MAIL_FROM=os.getenv("MAIL_FROM")
os.makedirs(FEE_UPLOAD_FOLDER,exist_ok=True)