import pymysql
from pymysql.cursors import DictCursor
from config import (MYSQL_HOST,MYSQL_PORT,MYSQL_DB,CHATBOT_DB_USER,CHATBOT_DB_PASSWORD,
                    CHATBOT_SQL_USER,CHATBOT_SQL_PASSWORD)


def query(sql:str,params:tuple=()):
    conn=pymysql.connect(host=MYSQL_HOST,port=MYSQL_PORT,user=CHATBOT_DB_USER,password=CHATBOT_DB_PASSWORD,
                         database=MYSQL_DB,cursorclass=DictCursor,autocommit=True,
                         connect_timeout=5,read_timeout=10)
    try:
        with conn.cursor() as cur:
            cur.execute(sql,params)
            return cur.fetchall()
    finally:
        conn.close()


def scoped_query(sql:str,student_id:int,user_id:int):
    conn=pymysql.connect(host=MYSQL_HOST,port=MYSQL_PORT,user=CHATBOT_SQL_USER,password=CHATBOT_SQL_PASSWORD,
                         database=MYSQL_DB,cursorclass=DictCursor,autocommit=True,
                         connect_timeout=5,read_timeout=10)
    try:
        with conn.cursor() as cur:
            for stmt in ("SET SESSION TRANSACTION READ ONLY","SET SESSION MAX_EXECUTION_TIME=5000"):
                try:
                    cur.execute(stmt)
                except Exception:
                    pass
            cur.execute("SET @current_student_id=%s,@current_user_id=%s",(int(student_id),int(user_id)))
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()