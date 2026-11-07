# from db.session import mysql
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import date
# import logging
# class MainModel:

#     @staticmethod
#     def get_user_by_email(email):
#         try:
#             conn=mysql.get_dict_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('SELECT * FROM users WHERE email=%s AND is_deleted=0',(email,))
#                 user=cursor.fetchone()
#                 return user
#         finally:
#             conn.close()
        


#     @staticmethod
#     def insert_user(email,password,role_id):
#         hashed_password=generate_password_hash(password)
#         try:
#             conn=mysql.get_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('INSERT INTO users(email,password,role_id) VALUES (%s,%s,%s)',(email,hashed_password,role_id))
#                 user_id=cursor.lastrowid
#                 conn.commit()
#                 return user_id
#         except Exception as e:
#             print(f"Error during insert user(models): {str(e)}")
#             conn.rollback()    
#         finally:
#             conn.close()    

#     @staticmethod
#     def insert_student(user_id,first_name,last_name,contact,email):
#         try:
#             conn=mysql.get_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('INSERT INTO students(user_id,first_name,last_name,contact,email,program_id,admission_date) VALUES (%s,%s,%s,%s,%s,%s,%s)',
#                        (user_id,first_name,last_name,contact,email,1,date.today()))
#                 conn.commit()
#         except Exception as e:
#             print(f"Error during insert student(models): {str(e)}")
#             conn.rollback()
#         finally:
#             conn.close()            
                


#     @staticmethod
#     def insert_teacher(user_id,first_name,last_name,contact,email):
#         try:
#             conn=mysql.get_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('INSERT INTO teachers(user_id,first_name,last_name,email,contact_num,joining_date) VALUES (%s,%s,%s,%s,%s,%s)',
#                        (user_id,first_name,last_name,email,contact,date.today()))
#                 conn.commit()
#         except Exception as e:
#             print(f"Error during insert teacher(models): {str(e)}")
#             conn.rollback()
#         finally:
#             conn.close()            
        


#     @staticmethod
#     def get_email_from_users(email):
#         try:
#             conn=mysql.get_dict_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('SELECT email FROM users WHERE email=%s AND is_deleted=0',(email,))
#                 user=cursor.fetchone()
#                 return user
#         except Exception as e:
#             print(f"Error during email from user(model): {str(e)}")
#         finally:
#             conn.close()        


#     @staticmethod
#     def update_password(email,new_password):
#         hash_password=generate_password_hash(new_password)
#         try:
#             conn=mysql.get_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('UPDATE users SET password=%s WHERE email=%s',(hash_password,email))
#                 conn.commit()
#         except Exception as e:
#             print(f"Error during updt passwrd: {str(e)}")
#             conn.rollback()
#         finally:
#             conn.close()      


#     @staticmethod
#     def insert_otp(user_id,otp,expire_at):
#         try:
#             conn=mysql.get_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('DELETE FROM reset_otps WHERE user_id=%s',(user_id,))
#                 cursor.execute('INSERT INTO reset_otps(otp_num,user_id,otp_expire) VALUES(%s,%s,%s)',(otp,user_id,expire_at))
#                 conn.commit()
#         except Exception as e:
#             logging.exception(f"during insrt otp(main): {str(e)}")
#             conn.rollback()
#             raise
#         finally:
#             conn.close()


#     @staticmethod
#     def get_otp(user_id):
#         try:
#             conn=mysql.get_dict_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('SELECT * FROM reset_otps WHERE user_id=%s ORDER BY otp_id DESC LIMIT 1',(user_id,))
#                 return cursor.fetchone()
#         except Exception as e:
#             logging.exception(f"during get otp(main): {str(e)}")
#             raise
#         finally:
#             conn.close()


#     @staticmethod
#     def increment_otp_attempts(otp_id):
#         try:
#             conn=mysql.get_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('UPDATE reset_otps SET otp_attempts=otp_attempts+1 WHERE otp_id=%s',(otp_id,))
#                 conn.commit()
#         finally:
#             conn.close()


#     @staticmethod
#     def mark_otp_used(otp_id):
#         try:
#             conn=mysql.get_connection()
#             with conn.cursor() as cursor:
#                 cursor.execute('UPDATE reset_otps SET otp_used=1 WHERE otp_id=%s',(otp_id,))
#                 conn.commit()
#         except Exception as e:
#             logging.exception(f"during mark otp used(main): {str(e)}")
#             conn.rollback()
#             raise
#         finally:
#             conn.close()





import logging
from datetime import date,time,timedelta

from sqlalchemy import select,update,delete
from werkzeug.security import generate_password_hash

from db.session import SessionLocal
from db.models.orm import User,Student,Teacher,ResetOtp


def _clean(value):
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, time):
        return timedelta(hours=value.hour,minutes=value.minute,
                         seconds=value.second,microseconds=value.microsecond)
    return value


def _obj(obj):
    return None if obj is None else {c.name: _clean(getattr(obj, c.name)) for c in obj.__table__.columns}


class MainModel:

    @staticmethod
    def get_user_by_email(email):
        session=SessionLocal()
        try:
            stmt=select(User).where(User.email==email, User.is_deleted==0)
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Error during get_user_by_email(auth): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def insert_user(email,password,role_id):
        hashed_password=generate_password_hash(password)
        session=SessionLocal()
        try:
            user=User(email=email,password=hashed_password,role_id=role_id)
            session.add(user)
            session.flush()
            user_id=user.user_id
            session.commit()
            return user_id
        except Exception as e:
            logging.exception(f"Error during insert_user(auth): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def insert_student(user_id,first_name,last_name,contact,email):
        session = SessionLocal()
        try:
            session.add(Student(user_id=user_id,first_name=first_name,last_name=last_name,
                                contact=str(contact),email=email,program_id=1,
                                admission_date=date.today()))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during insert_student(auth): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def insert_teacher(user_id,first_name,last_name,contact,email):
        session=SessionLocal()
        try:
            session.add(Teacher(user_id=user_id,first_name=first_name,last_name=last_name,
                                email=email,contact_num=str(contact),
                                joining_date=date.today()))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during insert_teacher(auth): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_email_from_users(email):
        session=SessionLocal()
        try:
            stmt=select(User.email).where(User.email==email, User.is_deleted==0)
            row = session.execute(stmt).first()
            return None if row is None else {'email': row[0]}
        except Exception as e:
            logging.exception(f"Error during get_email_from_users(auth): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def update_password(email,new_password):
        hashed_password = generate_password_hash(new_password)
        session = SessionLocal()
        try:
            session.execute(update(User).where(User.email == email).values(password=hashed_password))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during update_password(auth): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def insert_otp(user_id, otp, expire_at):
        session = SessionLocal()
        try:
            session.execute(delete(ResetOtp).where(ResetOtp.user_id == user_id))
            session.add(ResetOtp(otp_num=int(otp), user_id=user_id, otp_expire=expire_at))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during insert_otp(auth): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_otp(user_id):
        session = SessionLocal()
        try:
            stmt = (select(ResetOtp).where(ResetOtp.user_id == user_id)
                    .order_by(ResetOtp.otp_id.desc()).limit(1))
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Error during get_otp(auth): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def increment_otp_attempts(otp_id):
        session = SessionLocal()
        try:
            session.execute(update(ResetOtp).where(ResetOtp.otp_id == otp_id)
                            .values(otp_attempts=ResetOtp.otp_attempts + 1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during increment_otp_attempts(auth): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def mark_otp_used(otp_id):
        session = SessionLocal()
        try:
            session.execute(update(ResetOtp).where(ResetOtp.otp_id == otp_id).values(otp_used=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during mark_otp_used(auth): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()