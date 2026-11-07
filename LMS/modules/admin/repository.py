import logging
from datetime import datetime,time,timedelta

from sqlalchemy import select,update,delete,func,and_,or_
from sqlalchemy.orm import aliased

from db.session import SessionLocal
from db.models.orm import (  
    User,UserRole,Admin,Student,Teacher,Program,Course,TeacherCourse,
    StudentCourse,StudentSection,Section,CourseSchedule,Attendance,
    CourseAttendanceLog,StudentResult,StudentResultMarks,StudentFee,
    Semester,SummerSemester,SummerRegistration,SemesterFreezeStudent,
    FypGroup,Exam,Notification,ComplaintSuggestion,SystemSetting,
    TeacherSalary,
)


def _clean(value):
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, time):
        return timedelta(hours=value.hour, minutes=value.minute,
                         seconds=value.second, microseconds=value.microsecond)
    return value


def _row(row):
    return None if row is None else {k: _clean(v) for k, v in row._mapping.items()}


def _rows(rows):
    return [_row(r) for r in rows]


def _obj(obj):
    return None if obj is None else {c.name: _clean(getattr(obj, c.name)) for c in obj.__table__.columns}


def _objs(objs):
    return [_obj(o) for o in objs]


class UserModel:

    @staticmethod
    def get_by_email(email):
        session=SessionLocal()
        try:
            stmt=select(User).where(User.email==email,User.is_deleted==0)
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Err during gtbyeml(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def update_email(user_id,email):
        session=SessionLocal()
        try:
            session.execute(update(User)
                            .where(User.user_id==user_id,User.is_deleted==0)
                            .values(email=email))
            session.commit()
        except Exception as e:
            logging.exception(f"Err during updtemil(model): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def soft_delete(email):
        session=SessionLocal()
        try:
            session.execute(update(User).where(User.email==email).values(is_deleted=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete user(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def create(email,password_hash,role_id):
        session=SessionLocal()
        try:
            user=User(email=email,password=password_hash,role_id=role_id)
            session.add(user)
            session.flush()
            user_id=user.user_id
            session.commit()
            return user_id
        except Exception as e:
            logging.exception(f"Error during user create(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def email_exists(email):
        session=SessionLocal()
        try:
            stmt=select(User.user_id).where(User.email==email,User.is_deleted==0)
            return _row(session.execute(stmt).first())
        except Exception as e:
            logging.exception(f"Error during email_exists(admin_models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=(select(User.user_id,User.email,UserRole.role_type)
                  .select_from(User)
                  .join(UserRole,User.role_id==UserRole.role_id)
                  .where(User.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all users(admin_models): {str(e)}")
            raise
        finally:
            session.close()


class AdminModel:

    @staticmethod
    def get_admin_by_email(email):
        session=SessionLocal()
        try:
            stmt=select(Admin).where(Admin.email==email,Admin.is_deleted==0)
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Error during get_by_email admin(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_email_by_user_id(user_id:int):
        session=SessionLocal()
        try:
            stmt=select(User.email).where(User.user_id==user_id,User.is_deleted==0)
            row=_row(session.execute(stmt).first())
            return row['email'] if row else None
        except Exception as e:
            logging.exception(f"Error during get email by user id(models): {str(e)}")
            return None
        finally:
            session.close()



    @staticmethod
    def get_by_id(admin_id):
        session=SessionLocal()
        try:
            stmt=select(Admin).where(Admin.admin_id==admin_id,Admin.is_deleted==0)
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Error during get_by_id admin(admin_models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def update(admin_id,email,first_name,last_name,contact):
        session=SessionLocal()
        try:
            session.execute(update(Admin)
                            .where(Admin.admin_id==admin_id,Admin.is_deleted==0)
                            .values(email=email,first_name=first_name,
                                    last_name=last_name,contact=contact))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during update admin(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()



    @staticmethod
    def get_dashboard_counts():
        session=SessionLocal()
        try:
            keys=['students','teachers','pending_fees','courses','fyp','complaints','freeze','exams','notifications']
            queries=[
                select(func.count().label('c')).select_from(Student).where(Student.is_deleted==0),
                select(func.count().label('c')).select_from(Teacher).where(Teacher.is_deleted==0),
                select(func.count().label('c')).select_from(StudentFee).where(StudentFee.fee_status=='due'),
                select(func.count().label('c')).select_from(Course).where(Course.is_deleted==0),
                select(func.count().label('c')).select_from(FypGroup).where(FypGroup.is_deleted==0),
                select(func.count().label('c')).select_from(ComplaintSuggestion),
                select(func.count().label('c')).select_from(SemesterFreezeStudent).where(SemesterFreezeStudent.status=='Pending'),
                select(func.count().label('c')).select_from(Exam).where(Exam.status=='Ongoing',Exam.is_deleted==0),
                select(func.count().label('c')).select_from(Notification).where(Notification.status=='Pending',Notification.is_deleted==0),
            ]
            counts={}
            for key,stmt in zip(keys,queries):
                counts[key]=_row(session.execute(stmt).first())['c']
            return counts
        except Exception as e:
            logging.exception(f"Error during get_dashboard_counts(admin_models): {str(e)}")
            raise
        finally:
            session.close()


class SystemModel:

    @staticmethod
    def get_all_settings():
        session=SessionLocal()
        try:
            return _objs(session.execute(select(SystemSetting)).scalars().all())
        except Exception as e:
            logging.exception(f"Error during get_all_settings(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def update_setting(setting_key, new_value):
        session=SessionLocal()
        try:
            session.execute(update(SystemSetting)
                            .where(SystemSetting.setting_key==setting_key)
                            .values(setting_value=new_value))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during update_setting(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class ComplaintModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            # cs.*, u.email
            stmt=(select(*ComplaintSuggestion.__table__.columns,User.email)
                  .select_from(ComplaintSuggestion)
                  .join(User,ComplaintSuggestion.user_id==User.user_id))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all complaints(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def mark_solved(complt_sugst_id):
        session=SessionLocal()
        try:
            session.execute(update(ComplaintSuggestion)
                            .where(ComplaintSuggestion.complt_sugst_id==complt_sugst_id)
                            .values(is_status='Solved'))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during mark_solved(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class StudentModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            # ss.*, p.program_name, u.email  (original me u.email, students.email ko override karta tha,
            # isliye students ka email column star se nikal ke users ka email rakha hai)
            student_cols=[c for c in Student.__table__.columns if c.name!='email']
            stmt=(select(*student_cols,Program.program_name,User.email)
                  .select_from(Student)
                  .join(Program,Student.program_id==Program.program_id)
                  .join(User,Student.user_id==User.user_id)
                  .where(Student.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all students(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_by_id(student_id):
        session=SessionLocal()
        try:
            stmt=select(Student).where(Student.student_id==student_id)
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Error during get_by_id student(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_user_id(student_id):
        session=SessionLocal()
        try:
            stmt=select(Student.user_id).where(Student.student_id==student_id,Student.is_deleted==0)
            return _row(session.execute(stmt).first())['user_id']
        except Exception as e:
            logging.exception(f"Error during get_user_id student(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_admission_sessions():
        session=SessionLocal()
        try:
            stmt=(select(Student.admission_session).distinct()
                  .where(Student.admission_session.is_not(None)))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_admission_sessions(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def create(user_id, first_name, last_name, email, contact, program_id, admission_session, last_qual, admission_date, current_semester):
        session=SessionLocal()
        try:
            session.add(Student(user_id=user_id,first_name=first_name,last_name=last_name,
                                contact=contact,email=email,last_qualification=last_qual,
                                program_id=program_id,admission_session=admission_session,
                                admission_date=admission_date,current_semester=current_semester))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during student create(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update(student_id, first_name, last_name, email, contact, program_id, admission_session, last_qualification, admission_date):
        session=SessionLocal()
        try:
            session.execute(update(Student)
                            .where(Student.student_id==student_id)
                            .values(first_name=first_name,last_name=last_name,email=email,
                                    contact=contact,program_id=program_id,
                                    admission_session=admission_session,
                                    last_qualification=last_qualification,
                                    admission_date=admission_date))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during student update(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def soft_delete(student_id):
        session=SessionLocal()
        try:
            session.execute(update(Student).where(Student.student_id==student_id).values(is_deleted=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete student(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def promote(student_id):
        session=SessionLocal()
        try:
            session.execute(update(Student)
                            .where(Student.student_id==student_id)
                            .values(current_semester=Student.current_semester+1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during promote student(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_with_results():
        session=SessionLocal()
        try:
            sr2=aliased(StudentResult)
            max_sem=(select(func.max(sr2.student_semester))
                     .where(sr2.student_id==Student.student_id)
                     .correlate(Student)
                     .scalar_subquery())

            stmt=(select(Student.student_id,Student.first_name,Student.last_name,Student.current_semester,
                         StudentResult.result_status,StudentResult.overall_gpa,
                         StudentResult.student_semester,Program.program_name)
                  .select_from(Student)
                  .join(Program,Student.program_id==Program.program_id)
                  .outerjoin(StudentResult,and_(Student.student_id==StudentResult.student_id,
                                                StudentResult.student_semester==max_sem))
                  .where(Student.is_deleted==0)
                  .order_by(Student.student_id.asc()))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_with_results(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_result_by_id(student_id):
        session=SessionLocal()
        try:
            stmt=(select(StudentResult.result_status,StudentResult.student_semester)
                  .where(StudentResult.student_id==student_id)
                  .order_by(StudentResult.student_semester.asc())
                  .limit(1))
            return _row(session.execute(stmt).first())
        except Exception as e:
            logging.exception(f"Error during get_result_by_id(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def count_active():
        session=SessionLocal()
        try:
            stmt=select(func.count().label('total')).select_from(Student).where(Student.is_deleted==0)
            return _row(session.execute(stmt).first())['total']
        except Exception as e:
            logging.exception(f"Error during count_active students(admin_models): {str(e)}")
            raise
        finally:
            session.close()


class TeacherModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=(select(Teacher.teacher_id,Teacher.first_name,Teacher.last_name,Teacher.email,
                         Teacher.contact_num,Teacher.qualification,Teacher.joining_date)
                  .where(Teacher.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all teachers(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_by_id(teacher_id):
        session=SessionLocal()
        try:
            stmt=select(Teacher).where(Teacher.teacher_id==teacher_id)
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Error during get_by_id teacher(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_user_id(teacher_id):
        session=SessionLocal()
        try:
            stmt=select(Teacher.user_id).where(Teacher.teacher_id==teacher_id)
            return _row(session.execute(stmt).first())['user_id']
        except Exception as e:
            logging.exception(f"Error during get_user_id teacher(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_courses(teacher_id):
        session=SessionLocal()
        try:
            stmt=(select(Course.course_name)
                  .select_from(TeacherCourse)
                  .join(Course,TeacherCourse.course_id==Course.course_id)
                  .where(TeacherCourse.teacher_id==teacher_id,TeacherCourse.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_courses(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def email_exists(email):
        session=SessionLocal()
        try:
            stmt=select(Teacher.email).where(Teacher.email==email,Teacher.is_deleted==0)
            return _row(session.execute(stmt).first())
        except Exception as e:
            logging.exception(f"Error during email_exists teacher(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def create(user_id, first_name, last_name, email, contact_num, qualification, joining_date):
        session=SessionLocal()
        try:
            teacher=Teacher(user_id=user_id,first_name=first_name,last_name=last_name,
                            email=email,contact_num=contact_num,qualification=qualification,
                            joining_date=joining_date)
            session.add(teacher)
            session.flush()
            teacher_id=teacher.teacher_id
            session.commit()
            return teacher_id
        except Exception as e:
            logging.exception(f"Error during teacher create(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update(user_id, first_name, last_name, email, contact_num, qualification, joining_date):
        session=SessionLocal()
        try:
            session.execute(update(Teacher)
                            .where(Teacher.user_id==user_id)
                            .values(first_name=first_name,last_name=last_name,email=email,
                                    contact_num=contact_num,qualification=qualification,
                                    joining_date=joining_date))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during teacher update(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def soft_delete(teacher_id):
        session=SessionLocal()
        try:
            session.execute(update(Teacher).where(Teacher.teacher_id==teacher_id).values(is_deleted=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete teacher(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def set_courses(teacher_id, course_ids):
        session=SessionLocal()
        try:
            session.execute(delete(TeacherCourse).where(TeacherCourse.teacher_id==teacher_id))
            for cid in course_ids:
                session.add(TeacherCourse(teacher_id=teacher_id,course_id=cid))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during set_courses(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_all_assignments():
        session=SessionLocal()
        try:
            stmt=(select(TeacherCourse.teacher_course_id,Teacher.first_name,Teacher.last_name,
                         Course.course_name,Course.credit_hours,Program.program_name)
                  .select_from(TeacherCourse)
                  .join(Teacher,TeacherCourse.teacher_id==Teacher.teacher_id)
                  .join(Course,TeacherCourse.course_id==Course.course_id)
                  .join(Program,Course.program_id==Program.program_id)
                  .where(TeacherCourse.is_deleted==0,Teacher.is_deleted==0,Course.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all_assignments(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def assign_course(teacher_id, course_id):
        session=SessionLocal()
        try:
            session.add(TeacherCourse(course_id=course_id,teacher_id=teacher_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during assign_course(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def remove_assignment(teacher_course_id):
        session=SessionLocal()
        try:
            session.execute(update(TeacherCourse)
                            .where(TeacherCourse.teacher_course_id==teacher_course_id)
                            .values(is_deleted=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during remove_assignment(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class SalaryModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            net_salary=(TeacherSalary.basic_salary+TeacherSalary.bonus-TeacherSalary.deductions).label('net_salary')
            stmt=(select(TeacherSalary.salary_id,Teacher.first_name,Teacher.last_name,
                         TeacherSalary.month,TeacherSalary.year,TeacherSalary.basic_salary,
                         TeacherSalary.bonus,TeacherSalary.deductions,net_salary,TeacherSalary.status)
                  .select_from(TeacherSalary)
                  .join(Teacher,TeacherSalary.teacher_id==Teacher.teacher_id)
                  .where(TeacherSalary.is_deleted==0)
                  .order_by(TeacherSalary.salary_id.asc()))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all salary(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def exists(teacher_id, month, year):
        session=SessionLocal()
        try:
            stmt=(select(TeacherSalary.salary_id)
                  .where(TeacherSalary.teacher_id==teacher_id,
                         TeacherSalary.month==month,
                         TeacherSalary.year==year))
            return _row(session.execute(stmt).first())
        except Exception as e:
            logging.exception(f"Error during salary exists(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def create(teacher_id, month, year, basic_salary, bonus, deductions, status):
        session=SessionLocal()
        try:
            session.add(TeacherSalary(teacher_id=teacher_id,month=month,year=year,
                                      basic_salary=basic_salary,bonus=bonus,
                                      deductions=deductions,status=status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during salary create(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update(salary_id, basic_salary, bonus, deductions, status):
        session=SessionLocal()
        try:
            session.execute(update(TeacherSalary)
                            .where(TeacherSalary.salary_id==salary_id)
                            .values(basic_salary=basic_salary,bonus=bonus,
                                    deductions=deductions,status=status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during salary update(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def soft_delete(salary_id):
        session=SessionLocal()
        try:
            session.execute(update(TeacherSalary)
                            .where(TeacherSalary.salary_id==salary_id)
                            .values(is_deleted=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete salary(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class EnrollmentModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=(select(StudentCourse.student_course_id,Student.first_name,Student.last_name,
                         Student.student_id,Course.course_name,Program.program_name)
                  .select_from(StudentCourse)
                  .join(Student,StudentCourse.student_id==Student.student_id)
                  .join(Course,StudentCourse.course_id==Course.course_id)
                  .join(Program,Student.program_id==Program.program_id)
                  .where(StudentCourse.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all enrollments(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def exists(student_id, course_id):
        session=SessionLocal()
        try:
            stmt=select(StudentCourse).where(StudentCourse.student_id==student_id,
                                             StudentCourse.course_id==course_id,
                                             StudentCourse.is_deleted==0)
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Error during enrollment exists(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def enroll(student_id, course_id):
        session=SessionLocal()
        try:
            session.add(StudentCourse(student_id=student_id,course_id=course_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during enroll(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def remove(student_course_id):
        session=SessionLocal()
        try:
            record=_row(session.execute(
                select(StudentCourse.student_id,StudentCourse.course_id)
                .where(StudentCourse.student_course_id==student_course_id)).first())
            session.execute(update(StudentCourse)
                            .where(StudentCourse.student_course_id==student_course_id)
                            .values(is_deleted=1))
            if record:
                course_sections=select(Section.section_id).where(Section.course_id==record['course_id'])
                session.execute(update(StudentSection)
                                .where(StudentSection.student_id==record['student_id'],
                                       StudentSection.section_id.in_(course_sections))
                                .values(is_deleted=1))
            session.commit()
            return record
        except Exception as e:
            logging.exception(f"Error during enrollment remove(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_section(student_id, section_id, is_deleted=0):
        session=SessionLocal()
        try:
            stmt=select(StudentSection).where(StudentSection.student_id==student_id,
                                              StudentSection.section_id==section_id,
                                              StudentSection.is_deleted==is_deleted)
            return _obj(session.execute(stmt).scalars().first())
        except Exception as e:
            logging.exception(f"Error during get_section(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def add_or_restore_section(student_id, section_id):
        session=SessionLocal()
        try:
            existing=session.execute(
                select(StudentSection).where(StudentSection.student_id==student_id,
                                             StudentSection.section_id==section_id,
                                             StudentSection.is_deleted==1)).scalars().first()
            if existing:
                session.execute(update(StudentSection)
                                .where(StudentSection.student_id==student_id,
                                       StudentSection.section_id==section_id)
                                .values(is_deleted=0))
            else:
                session.add(StudentSection(student_id=student_id,section_id=section_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during add_or_restore_section(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_all_sections():
        session=SessionLocal()
        try:
            stmt=select(Section.section_id,Section.section_name,Section.semester,Section.course_id)
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all_sections(admin_models): {str(e)}")
            raise
        finally:
            session.close()


class AttendanceModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=(select(Attendance.attendance_id,Attendance.attendance_date,Attendance.attendance_status,
                         Student.first_name,Student.last_name,Course.course_name,Section.section_name)
                  .select_from(Attendance)
                  .join(Student,Attendance.student_id==Student.student_id)
                  .join(StudentCourse,Attendance.student_course_id==StudentCourse.student_course_id)
                  .join(Course,StudentCourse.course_id==Course.course_id)
                  .join(CourseSchedule,Attendance.course_schedule_id==CourseSchedule.course_schedule_id)
                  .join(Section,CourseSchedule.section_id==Section.section_id)
                  .where(Attendance.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all attendance(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def update(attendance_id, status):
        session=SessionLocal()
        try:
            session.execute(update(Attendance)
                            .where(Attendance.attendance_id==attendance_id)
                            .values(attendance_status=status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during attendance update(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_all_course_logs():
        session=SessionLocal()
        try:
            stmt=(select(CourseAttendanceLog.log_id,CourseAttendanceLog.attendance_date,
                         CourseAttendanceLog.total_students,CourseAttendanceLog.total_present,
                         CourseAttendanceLog.total_absent,Teacher.first_name,Teacher.last_name,
                         Course.course_name,CourseSchedule.day_of_week)
                  .select_from(CourseAttendanceLog)
                  .join(Teacher,CourseAttendanceLog.teacher_id==Teacher.teacher_id)
                  .join(Course,CourseAttendanceLog.course_id==Course.course_id)
                  .join(CourseSchedule,CourseAttendanceLog.course_schedule_id==CourseSchedule.course_schedule_id)
                  .where(CourseAttendanceLog.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all_course_logs(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_schedule_by_section(section_id):
        session=SessionLocal()
        try:
            stmt=(select(CourseSchedule.course_schedule_id,Section.semester)
                  .select_from(CourseSchedule)
                  .join(Section,CourseSchedule.section_id==Section.section_id)
                  .where(CourseSchedule.section_id==section_id)
                  .limit(1))
            return _row(session.execute(stmt).first())
        except Exception as e:
            logging.exception(f"Error during get_schedule_by_section(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def insert_course_log(teacher_id, course_id, course_schedule_id, attendance_date, semester, total_students, total_present, total_absent):
        session=SessionLocal()
        try:
            session.add(CourseAttendanceLog(teacher_id=teacher_id,course_id=course_id,
                                            course_schedule_id=course_schedule_id,
                                            attendance_date=attendance_date,semester=semester,
                                            total_students=total_students,
                                            total_present=total_present,
                                            total_absent=total_absent))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during insert_course_log(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class GradeModel:

    @staticmethod
    def get_results(program_id=None, selected_semester=None):
        session=SessionLocal()
        try:
            stmt=(select(StudentResult.student_result_id,StudentResult.student_id,
                         StudentResult.student_semester,StudentResult.overall_gpa,
                         StudentResult.result_status,Student.first_name,Student.last_name)
                  .select_from(StudentResult)
                  .join(Student,StudentResult.student_id==Student.student_id)
                  .join(Program,Student.program_id==Program.program_id))
            if program_id:
                stmt=stmt.where(Program.program_id==program_id)
            if selected_semester:
                stmt=stmt.where(StudentResult.student_semester==selected_semester)
            stmt=stmt.order_by(StudentResult.student_semester.asc())
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_results(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_marks(student_result_id):
        session=SessionLocal()
        try:
            # srm.*, c.course_name
            stmt=(select(*StudentResultMarks.__table__.columns,Course.course_name)
                  .select_from(StudentResultMarks)
                  .join(StudentCourse,StudentResultMarks.student_course_id==StudentCourse.student_course_id)
                  .join(Course,StudentCourse.course_id==Course.course_id)
                  .where(StudentResultMarks.student_result_id==student_result_id))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_marks(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def update(student_result_id, overall_gpa, result_status):
        session=SessionLocal()
        try:
            session.execute(update(StudentResult)
                            .where(StudentResult.student_result_id==student_result_id)
                            .values(overall_gpa=overall_gpa,result_status=result_status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during grade update(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class FeeModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            # sf.*, p.program_name, s.first_name, s.last_name
            stmt=(select(*StudentFee.__table__.columns,Program.program_name,
                         Student.first_name,Student.last_name)
                  .select_from(StudentFee)
                  .join(Student,StudentFee.student_id==Student.student_id)
                  .join(Program,StudentFee.program_id==Program.program_id))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all fees(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def update_status(student_fees_id, fee_status):
        session=SessionLocal()
        try:
            session.execute(update(StudentFee)
                            .where(StudentFee.student_fees_id==student_fees_id)
                            .values(fee_status=fee_status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during fee update_status(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def create(student_id, program_id, fee_amount, fee_month, fee_status):
        session=SessionLocal()
        try:
            session.add(StudentFee(student_id=student_id,program_id=program_id,
                                   fee_amount=fee_amount,fee_month=fee_month,
                                   fee_status=fee_status,update_date=func.now()))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during fee create(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class SemesterModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=select(Semester).where(Semester.is_deleted==0)
            return _objs(session.execute(stmt).scalars().all())
        except Exception as e:
            logging.exception(f"Error during get_all semesters(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def create(name, year, start_date, end_date):
        session=SessionLocal()
        try:
            session.add(Semester(name=name,year=year,start_date=start_date,
                                 end_date=end_date,created_at=datetime.now()))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during semester create(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update(semester_id, name, year, start_date, end_date):
        session=SessionLocal()
        try:
            session.execute(update(Semester)
                            .where(Semester.semester_id==semester_id)
                            .values(name=name,year=year,start_date=start_date,
                                    end_date=end_date,created_at=datetime.now()))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during semester update(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def soft_delete(semester_id):
        session=SessionLocal()
        try:
            session.execute(update(Semester)
                            .where(Semester.semester_id==semester_id)
                            .values(is_deleted=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete semester(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_all_summer():
        session=SessionLocal()
        try:
            stmt=(select(SummerSemester)
                  .order_by(SummerSemester.year.desc(),SummerSemester.summer_semesters_id.desc()))
            return _objs(session.execute(stmt).scalars().all())
        except Exception as e:
            logging.exception(f"Error during get_all_summer(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def get_summer_registrations(summer_semesters_id):
        session=SessionLocal()
        try:
            stmt=(select(Student.first_name,Student.last_name,Course.course_name,
                         SummerRegistration.registration_date)
                  .select_from(SummerRegistration)
                  .join(Student,SummerRegistration.student_id==Student.student_id)
                  .join(Course,SummerRegistration.course_id==Course.course_id)
                  .where(SummerRegistration.summer_semesters_id==summer_semesters_id))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_summer_registrations(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def create_summer(name, year, start_date, end_date, status, previous_semester_id):
        session=SessionLocal()
        try:
            session.add(SummerSemester(name=name,year=year,start_date=start_date,
                                       end_date=end_date,status=status,
                                       previous_semester_id=previous_semester_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during create_summer(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def delete_summer(summer_semesters_id):
        session=SessionLocal()
        try:
            session.execute(delete(SummerSemester)
                            .where(SummerSemester.summer_semesters_id==summer_semesters_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during delete_summer(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_all_freeze_requests():
        session=SessionLocal()
        try:
            stmt=(select(SemesterFreezeStudent.freeze_id,SemesterFreezeStudent.semester,
                         SemesterFreezeStudent.reason,SemesterFreezeStudent.status,
                         SemesterFreezeStudent.applied_date,
                         Student.first_name,Student.last_name,Student.student_id)
                  .select_from(SemesterFreezeStudent)
                  .join(Student,SemesterFreezeStudent.student_id==Student.student_id))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all_freeze_requests(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def update_freeze_status(freeze_id, status):
        session=SessionLocal()
        try:
            session.execute(update(SemesterFreezeStudent)
                            .where(SemesterFreezeStudent.freeze_id==freeze_id)
                            .values(status=status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during update_freeze_status(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class TimetableModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=(select(CourseSchedule.course_schedule_id,CourseSchedule.day_of_week,
                         CourseSchedule.start_time,CourseSchedule.end_time,CourseSchedule.location,
                         Course.course_name,Section.section_name)
                  .select_from(CourseSchedule)
                  .join(Course,CourseSchedule.course_id==Course.course_id)
                  .join(Section,CourseSchedule.section_id==Section.section_id)
                  .where(CourseSchedule.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all timetable(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def exists(course_id):
        session=SessionLocal()
        try:
            stmt=select(CourseSchedule.course_id).where(CourseSchedule.course_id==course_id)
            return _row(session.execute(stmt).first())
        except Exception as e:
            logging.exception(f"Error during timetable exists(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def create(day_of_week, start_time, end_time, location, course_id, section_id):
        session=SessionLocal()
        try:
            session.add(CourseSchedule(day_of_week=day_of_week,start_time=start_time,
                                       end_time=end_time,location=location,
                                       course_id=course_id,section_id=section_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during timetable create(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update(course_schedule_id, day_of_week, start_time, end_time, location):
        session=SessionLocal()
        try:
            session.execute(update(CourseSchedule)
                            .where(CourseSchedule.course_schedule_id==course_schedule_id)
                            .values(day_of_week=day_of_week,start_time=start_time,
                                    end_time=end_time,location=location))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during timetable update(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def soft_delete(course_schedule_id):
        session=SessionLocal()
        try:
            session.execute(update(CourseSchedule)
                            .where(CourseSchedule.course_schedule_id==course_schedule_id)
                            .values(is_deleted=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete timetable(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class FYPModel:

    @staticmethod
    def get_all(status_filter=None):
        session=SessionLocal()
        try:
            stmt=(select(FypGroup.fyp_id,FypGroup.project_title,FypGroup.progress,FypGroup.description,
                         FypGroup.status,FypGroup.last_submission,FypGroup.created_at,
                         FypGroup.student_id,FypGroup.teacher_id,
                         func.concat(Student.first_name,' ',Student.last_name).label('student_name'),
                         Student.email.label('student_email'),
                         Student.contact.label('student_contact'),
                         Program.program_name.label('program'),
                         Section.semester,
                         func.concat(Teacher.first_name,' ',Teacher.last_name).label('teacher_name'),
                         Teacher.email.label('teacher_email'),
                         Teacher.contact_num.label('teacher_contact'))
                  .select_from(FypGroup)
                  .join(Student,FypGroup.student_id==Student.student_id)
                  .join(Teacher,FypGroup.teacher_id==Teacher.teacher_id)
                  .join(Program,Student.program_id==Program.program_id)
                  .outerjoin(StudentSection,and_(Student.student_id==StudentSection.student_id,
                                                 StudentSection.is_deleted==0))
                  .outerjoin(Section,StudentSection.section_id==Section.section_id)
                  .where(FypGroup.is_deleted==0))
            if status_filter:
                stmt=stmt.where(FypGroup.status==status_filter)
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all fyp(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def update_status(fyp_id, status):
        session=SessionLocal()
        try:
            session.execute(update(FypGroup).where(FypGroup.fyp_id==fyp_id).values(status=status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during update_status fyp(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def assign_supervisor(fyp_id, teacher_id):
        session=SessionLocal()
        try:
            session.execute(update(FypGroup).where(FypGroup.fyp_id==fyp_id).values(teacher_id=teacher_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during assign_supervisor(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class ExamModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=(select(Exam.exam_id,Exam.exam_category,Exam.exam_date,Exam.exam_semester,
                         Exam.start_time,Exam.end_time,Exam.location,Exam.mode,Exam.status,
                         Program.program_name)
                  .select_from(Exam)
                  .join(Program,Exam.program_id==Program.program_id)
                  .where(Exam.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all exams(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def exists(program_id, exam_category, exam_semester, exam_date):
        session=SessionLocal()
        try:
            stmt=select(Exam.exam_id).where(Exam.program_id==program_id,
                                            Exam.exam_category==exam_category,
                                            Exam.exam_semester==exam_semester,
                                            Exam.exam_date==exam_date)
            return _row(session.execute(stmt).first())
        except Exception as e:
            logging.exception(f"Error during exam exists(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def create(program_id, exam_category, exam_date, exam_semester, start_time, end_time, location, mode):
        session=SessionLocal()
        try:
            session.add(Exam(program_id=program_id,exam_category=exam_category,exam_date=exam_date,
                             exam_semester=exam_semester,start_time=start_time,end_time=end_time,
                             location=location,mode=mode,status='Ongoing'))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during exam create(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def update(exam_id, exam_category, exam_date, exam_semester, start_time, end_time, location, mode, status):
        session=SessionLocal()
        try:
            session.execute(update(Exam)
                            .where(Exam.exam_id==exam_id,Exam.is_deleted==0)
                            .values(exam_category=exam_category,exam_date=exam_date,
                                    exam_semester=exam_semester,start_time=start_time,
                                    end_time=end_time,location=location,mode=mode,status=status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during exam update(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def soft_delete(exam_id):
        session=SessionLocal()
        try:
            session.execute(update(Exam).where(Exam.exam_id==exam_id).values(is_deleted=1))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete exam(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class NotificationModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=(select(Notification.id,Notification.title,Notification.sender_role,
                         Notification.receiver_role,Notification.status,Notification.created_at)
                  .where(Notification.is_deleted==0))
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all notifications(admin_models): {str(e)}")
            raise
        finally:
            session.close()

    @staticmethod
    def send(sender_id, sender_role, receiver_id, receiver_role, title, description, related_course_id):
        session=SessionLocal()
        try:
            session.add(Notification(sender_id=sender_id,sender_role=sender_role,
                                     receiver_id=receiver_id,receiver_role=receiver_role,
                                     title=title,description=description,
                                     related_course_id=related_course_id,status='Pending'))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during notification send(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def soft_delete(notify_id):
        session=SessionLocal()
        try:
            session.execute(update(Notification)
                            .where(Notification.id==notify_id)
                            .values(is_deleted=1,status='Rejected'))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete notification(admin_models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


class ProgramModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=select(Program).where(Program.is_deleted==0)
            return _objs(session.execute(stmt).scalars().all())
        except Exception as e:
            logging.exception(f"Error during get_all programs(admin_models): {str(e)}")
            raise
        finally:
            session.close()


class CourseModel:

    @staticmethod
    def get_all():
        session=SessionLocal()
        try:
            stmt=select(Course.course_id,Course.course_name).where(Course.is_deleted==0)
            return _rows(session.execute(stmt).all())
        except Exception as e:
            logging.exception(f"Error during get_all courses(admin_models): {str(e)}")
            raise
        finally:
            session.close()







class EmailLookup:
    @staticmethod
    def _one(stmt):
        session=SessionLocal()
        try:
            row=_row(session.execute(stmt).first())
            return row['email'] if row else None
        except Exception as e:
            logging.exception(f"Error during email lookup(models): {str(e)}")
            return None
        finally:
            session.close()

    @staticmethod
    def by_freeze_id(freeze_id):
        return EmailLookup._one(
            select(User.email)
            .select_from(SemesterFreezeStudent)
            .join(Student,SemesterFreezeStudent.student_id==Student.student_id)
            .join(User,Student.user_id==User.user_id)
            .where(SemesterFreezeStudent.freeze_id==freeze_id))

    @staticmethod
    def by_fyp_id(fyp_id):
        return EmailLookup._one(
            select(User.email)
            .select_from(FypGroup)
            .join(Student,FypGroup.student_id==Student.student_id)
            .join(User,Student.user_id==User.user_id)
            .where(FypGroup.fyp_id==fyp_id))

    @staticmethod
    def by_complaint_id(complaint_id):
        return EmailLookup._one(
            select(User.email)
            .select_from(ComplaintSuggestion)
            .join(User,ComplaintSuggestion.user_id==User.user_id)
            .where(ComplaintSuggestion.complt_sugst_id==complaint_id))