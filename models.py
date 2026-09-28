from utils.db import mysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

class MainModel:

    @staticmethod
    def get_user_by_email(email):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE email=%s AND is_deleted=0',(email,))
                user=cursor.fetchone()
                return user
        finally:
            conn.close()
        


    @staticmethod
    def insert_user(email,password,role_id):
        hashed_password=generate_password_hash(password)
        try:
            conn=mysql.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO users(email,password,role_id) VALUES (%s,%s,%s)',(email,hashed_password,role_id))
                user_id=cursor.lastrowid
                conn.commit()
                return user_id
        except Exception as e:
            print(f"Error during insert user(models): {str(e)}")
            conn.rollback()    
        finally:
            conn.close()    

    @staticmethod
    def insert_student(user_id,first_name,last_name,contact,email):
        try:
            conn=mysql.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO students(user_id,first_name,last_name,contact,email,program_id,admission_date) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                       (user_id,first_name,last_name,contact,email,1,date.today()))
                conn.commit()
        except Exception as e:
            print(f"Error during insert student(models): {str(e)}")
            conn.rollback()
        finally:
            conn.close()            
                


    @staticmethod
    def insert_teacher(user_id,first_name,last_name,contact,email):
        try:
            conn=mysql.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO teachers(user_id,first_name,last_name,email,contact_num,joining_date) VALUES (%s,%s,%s,%s,%s,%s)',
                       (user_id,first_name,last_name,email,contact,date.today()))
                conn.commit()
        except Exception as e:
            print(f"Error during insert teacher(models): {str(e)}")
            conn.rollback()
        finally:
            conn.close()            
        


    @staticmethod
    def get_email_from_users(email):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT email FROM users WHERE email=%s AND is_deleted=0',(email,))
                user=cursor.fetchone()
                return user
        except Exception as e:
            print(f"Error during email from user(model): {str(e)}")
        finally:
            conn.close()        


    @staticmethod
    def update_password(email,new_password):
        hash_password=generate_password_hash(new_password)
        try:
            conn=mysql.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE users SET password=%s WHERE email=%s',(hash_password,email))
                conn.commit()
        except Exception as e:
            print(f"Error during updt passwrd: {str(e)}")
            conn.rollback()
        finally:
            conn.close()            
       




