from utils.db import mysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

class MainModel:

    @staticmethod
    def get_user_by_email(email):
        conn=mysql.get_dict_connection()
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email=%s AND is_deleted=0',(email,))
        user=cursor.fetchone()
        cursor.close()
        conn.close()
        return user


    @staticmethod
    def insert_user(email,password,role_id):
        hashed_password=generate_password_hash(password)
        conn=mysql.get_connection()
        cursor=conn.cursor()
        cursor.execute('INSERT INTO users(email,password,role_id) VALUES (%s,%s,%s)',(email,hashed_password,role_id))
        user_id=cursor.lastrowid
        cursor.close()
        conn.close()
        return user_id

    @staticmethod
    def insert_student(user_id,first_name,last_name,contact,email):
        conn=mysql.get_connection()
        cursor=conn.cursor()
        cursor.execute('INSERT INTO students(user_id,first_name,last_name,contact,email,program_id,admission_date) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                       (user_id,first_name,last_name,contact,email,1,date.today()))
        cursor.close()
        conn.close()


    @staticmethod
    def insert_teacher(user_id,first_name,last_name,contact,email):
        conn=mysql.get_connection()
        cursor=conn.cursor()
        cursor.execute('INSERT INTO teachers(user_id,first_name,last_name,email,contact_num,joining_date) VALUES (%s,%s,%s,%s,%s,%s)',
                       (user_id,first_name,last_name,email,contact,date.today()))
        cursor.close()
        conn.close()


    @staticmethod
    def get_email_from_users(email):
        conn=mysql.get_dict_connection()
        cursor=conn.cursor()
        cursor.execute('SELECT email FROM users WHERE email=%s AND is_deleted=0',(email,))
        user=cursor.fetchone()
        cursor.close()
        conn.close()
        return user

    @staticmethod
    def update_password(email,new_password):
        hash_password=generate_password_hash(new_password)
        conn=mysql.get_connection()
        cursor=conn.cursor()
        cursor.execute('UPDATE users SET password=%s WHERE email=%s',(hash_password,email))
        cursor.close()
        conn.close()




