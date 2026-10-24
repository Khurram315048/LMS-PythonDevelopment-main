from utils.db import mysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import logging
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


    @staticmethod
    def insert_otp(user_id,otp,expire_at):
        try:
            conn=mysql.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM reset_otps WHERE user_id=%s',(user_id,))
                cursor.execute('INSERT INTO reset_otps(otp_num,user_id,otp_expire) VALUES(%s,%s,%s)',(otp,user_id,expire_at))
                conn.commit()
        except Exception as e:
            logging.exception(f"during insrt otp(main): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


    @staticmethod
    def get_otp(user_id):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM reset_otps WHERE user_id=%s ORDER BY otp_id DESC LIMIT 1',(user_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"during get otp(main): {str(e)}")
            raise
        finally:
            conn.close()


    @staticmethod
    def increment_otp_attempts(otp_id):
        try:
            conn=mysql.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE reset_otps SET otp_attempts=otp_attempts+1 WHERE otp_id=%s',(otp_id,))
                conn.commit()
        finally:
            conn.close()


    @staticmethod
    def mark_otp_used(otp_id):
        try:
            conn=mysql.get_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE reset_otps SET otp_used=1 WHERE otp_id=%s',(otp_id,))
                conn.commit()
        except Exception as e:
            logging.exception(f"during mark otp used(main): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

