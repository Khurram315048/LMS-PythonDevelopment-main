from utils.db import mysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

class MainModel:

    @staticmethod
    def get_user_by_email(email):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email=%s',(email,))
        user=cursor.fetchone()
        return user


    @staticmethod
    def insert_user(email,password,role_id):
        hashed_password=generate_password_hash(password)
        cursor=mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO users(email,password,role_id) VALUES (%s,%s,%s)',
            (email,hashed_password,role_id)
        )
        mysql.connection.commit()
        user_id=cursor.lastrowid
        return user_id

    @staticmethod
    def insert_student(user_id):
        cursor=mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO students(user_id,program_id,admission_date) VALUES (%s,%s,%s)',
            (user_id,1,date.today())
        )
        mysql.connection.commit()

    @staticmethod
    def insert_teacher(user_id):
        cursor=mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO teachers(user_id,joining_date) VALUES (%s,%s)',
            (user_id,date.today())
        )
        mysql.connection.commit()


    @staticmethod
    def get_email_from_users(email):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT email FROM users WHERE email=%s',(email,))
        user=cursor.fetchone()
        return user

    @staticmethod
    def update_password(email,new_password):
        
        hash_password=generate_password_hash(new_password)
        cursor=mysql.connection.cursor()
        cursor.execute(
            'UPDATE users SET password=%s WHERE email=%s',
            (hash_password,email)
        )
        mysql.connection.commit()