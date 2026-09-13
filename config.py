
import secrets
import os
TEMPLATES_AUTO_RELOAD=True

MYSQL_HOST='172.25.0.2'
MYSQL_USER='root'
MYSQL_PASSWORD='root'
MYSQL_DB='lms_db'
MYSQL_PORT=3306
SECRET_KEY=secrets.token_hex(16)
MYSQL_CURSORCLASS='DictCursor'
BASE_DIR=os.path.abspath(os.path.dirname(__file__))
FEE_UPLOAD_FOLDER=os.path.join(BASE_DIR, "static", "uploads", "students_uploads", "voucher_pics")
os.makedirs(FEE_UPLOAD_FOLDER, exist_ok=True)