
import secrets
import os
import os
from dotenv import load_dotenv


load_dotenv()
TEMPLATES_AUTO_RELOAD=True

MYSQL_HOST=os.getenv('MYSQL_HOST','localhost')
MYSQL_USER=os.getenv('MYSQL_USER','root')
MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB=os.getenv('MYSQL_DB', 'lms')
MYSQL_PORT=int(os.getenv('MYSQL_PORT', 3306))
SECRET_KEY=os.getenv('SECRET_KEY') 
MYSQL_CURSORCLASS='DictCursor'
BASE_DIR=os.path.abspath(os.path.dirname(__file__))
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
FEE_UPLOAD_FOLDER=os.path.join(BASE_DIR, "static", "uploads", "students_uploads", "voucher_pics")
os.makedirs(FEE_UPLOAD_FOLDER, exist_ok=True)



