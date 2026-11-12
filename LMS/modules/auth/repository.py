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
        session=SessionLocal()
        try:
            session.execute(update(ResetOtp).where(ResetOtp.otp_id==otp_id)
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
        session=SessionLocal()
        try:
            session.execute(update(ResetOtp).where(ResetOtp.otp_id==otp_id).values(otp_used=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during mark_otp_used(auth): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()