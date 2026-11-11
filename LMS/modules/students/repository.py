from datetime import time, timedelta
import logging

from sqlalchemy import (
    select, update, delete, func, and_, or_, literal, literal_column, text, String,
)
from sqlalchemy.orm import aliased

from db.session import SessionLocal  
from db.models.orm import (
    User, Student, Program, Exam, Course, StudentCourse, TeacherCourse, Teacher,
    CourseSchedule, Section, StudentSection, StudentFee, ComplaintSuggestion,
    StudentSubmission, Attendance, StudentResult, StudentResultMarks,
    StudentImprovement, StudentFailSubject, Notification, SemesterFreezeStudent,
    SummerSemester, SummerRegistration, SystemSetting, FypGroup, FypMessage,
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


class CheckFreezeStatus:
    @staticmethod
    def confirm_freeze_status(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(SemesterFreezeStudent.status)
                  .where(SemesterFreezeStudent.student_id==student_id,
                         SemesterFreezeStudent.is_deleted.is_(False))
                  .order_by(SemesterFreezeStudent.applied_date.desc())
                  .limit(1))
            status=_row(session.execute(stmt).first())
            return status
        except Exception as e:
            logging.exception(f"Error during confirm freeze status(models): {str(e)}")
            raise
        finally:
            session.close()




class UserModel:
    @staticmethod
    def get_user_by_email(email:str):
        session=SessionLocal()
        try:
            stmt=select(User.user_id,User.password,User.role_id).where(User.email==email)
            user=_row(session.execute(stmt).first())
            return user
        except Exception as e:
            logging.exception(f"Error during user by email(models): {str(e)}")
            raise
        finally:
            session.close()


class StudentModel:
    @staticmethod
    def get_student_by_user_id(user_id:int):
        session=SessionLocal()
        try:
            stmt=select(Student).where(Student.user_id==user_id,Student.is_deleted.is_(False))
            student=_obj(session.execute(stmt).scalars().first())
            return student
        except Exception as e:
            logging.exception(f"Error during student by user_id(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_student_details(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(Student.student_id,Student.first_name,Student.last_name,
                         Student.current_semester,Program.program_name)
                  .select_from(Student)
                  .join(Program,Student.program_id==Program.program_id)
                  .where(Student.student_id==student_id))
            res=_row(session.execute(stmt).first())
            return res
        except Exception as e:
            logging.exception(f"Error during student details(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_student_by_id(student_id:int):
        session=SessionLocal()
        try:
            stmt=select(Student).where(Student.student_id==student_id,Student.is_deleted.is_(False))
            student=_obj(session.execute(stmt).scalars().first())
            return student
        except Exception as e:
            logging.exception(f"Error during student by id(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_student_name_by_user_id(user_id:int):
        session=SessionLocal()
        try:
            stmt=select(Student.first_name,Student.last_name,Student.student_id).where(Student.user_id==user_id)
            student_name=_row(session.execute(stmt).first())
            return student_name
        except Exception as e:
            logging.exception(f"Error during student name by user_id(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_program_id_student(student_id:int):
        session=SessionLocal()
        try:
            stmt=select(Student.program_id).where(Student.student_id==student_id)
            res=_row(session.execute(stmt).first())
            return res
        except Exception as e:
            logging.exception(f"Error during program_id student(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_exam_details_student(program_id:int):
        session=SessionLocal()
        try:
            stmt=(select(Exam.exam_id,Exam.exam_category,Exam.exam_date,Exam.exam_semester,
                         Exam.start_time,Exam.end_time,Exam.location,Exam.mode,Exam.status,
                         Program.program_name)
                  .select_from(Exam)
                  .join(Program,Exam.program_id==Program.program_id)
                  .where(Exam.program_id==program_id,Exam.is_deleted==0))
            res=_rows(session.execute(stmt).all())
            return res
        except Exception as e:
            logging.exception(f"Error during exam details(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_student_program_details(student_id:int):
        session=SessionLocal()
        try:
            student=_row(session.execute(
                select(Student.program_id).where(Student.student_id==student_id)).first())
            if student and student['program_id']:
                program=_obj(session.execute(
                    select(Program).where(Program.program_id==student['program_id'])).scalars().first())
                return program
            return None
        except Exception as e:
            logging.exception(f"Error during program details(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_enrolled_courses_by_student_id(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(Course.course_id,Course.course_name,Course.credit_hours).distinct()
                  .select_from(StudentCourse)
                  .join(Course,StudentCourse.course_id==Course.course_id)
                  .where(StudentCourse.student_id==student_id,
                         StudentCourse.is_deleted.is_(False),
                         Course.is_deleted.is_(False)))
            courses=_rows(session.execute(stmt).all())
            return courses
        except Exception as e:
            logging.exception(f"Error during enrolled courses(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_course_details_by_ids(course_ids:list):
        session=SessionLocal()
        try:
            if not course_ids:
                return []

            if not all(isinstance(id,int) and id>0 for id in course_ids):
                raise ValueError("Invalid course ids-must be positive")

            stmt=select(Course.course_id,Course.course_name).where(Course.course_id.in_(course_ids))
            course_data=_rows(session.execute(stmt).all())
            return course_data
        except ValueError as v:
            logging.warning(f"Error during course details(models): {str(v)}")
            return []
        except Exception as e:
            logging.exception(f"Error during course details(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_teachers_by_course_ids(course_ids:list):
        session=SessionLocal()
        try:
            if not course_ids:
                return []

            if not all(isinstance(id,int) and id>0 for id in course_ids):
                logging.warning(f"Error during course ids(models): {course_ids}")
                raise ValueError("Invalid course ids-must be positive")

            stmt=(select(TeacherCourse.course_id,TeacherCourse.teacher_id)
                  .where(TeacherCourse.course_id.in_(course_ids),TeacherCourse.is_deleted.is_(False)))
            teacher_rows=_rows(session.execute(stmt).all())
            return teacher_rows
        except ValueError as v:
            logging.warning(f"Error during course ids(models): {v}")
            return []
        except Exception as e:
            logging.exception(f"Error during teacher course ids: {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_teacher_info_by_ids(teacher_ids:list):
        session=SessionLocal()
        try:
            if not teacher_ids:
                return []

            if not all(isinstance(id,int) and id>0 for id in teacher_ids):
                logging.warning(f"Error during teacher info ids(models): {teacher_ids}")
                raise ValueError("Invalid ids-must be positive")

            stmt=(select(Teacher.teacher_id,Teacher.first_name,Teacher.last_name)
                  .where(Teacher.teacher_id.in_(teacher_ids),Teacher.is_deleted.is_(False)))
            teacher_data=_rows(session.execute(stmt).all())
            return teacher_data
        except ValueError as v:
            logging.warning(f"Error during teacher info ids(models): {v}")
            return []
        except Exception as e:
            logging.exception(f"Error during teacher info ids(models): {e}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_course_schedule_by_course_ids(course_ids:list):
        session=SessionLocal()
        try:
            if not course_ids:
                return []

            if not all(isinstance(id,int) and id>0 for id in course_ids):
                logging.warning(f"Error during teacher info ids(models): {course_ids}")
                raise ValueError("Invalid ids-must be positive")

            
            stmt=(select(*CourseSchedule.__table__.columns,
                         Section.assignments_enabled,Section.quizzes_enabled)
                  .select_from(CourseSchedule)
                  .join(Section,CourseSchedule.section_id==Section.section_id)
                  .where(CourseSchedule.course_id.in_(course_ids)))
            schedule=_rows(session.execute(stmt).all())
            return schedule
        except ValueError as v:
            logging.warning(f"Error during course schedule ids(models): {str(v)}")
            return []
        except Exception as e:
            logging.exception(f"Error during course schedule(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_course_schedule_for_enrolled_sections(course_ids:list,student_id:int):
        session=SessionLocal()
        try:
            if not course_ids:
                return []

            if not all(isinstance(id,int) and id>0 for id in course_ids):
                raise ValueError("Invalide ids-must be positive")

            stmt=(select(CourseSchedule.course_id,CourseSchedule.section_id,
                         CourseSchedule.day_of_week,CourseSchedule.start_time,CourseSchedule.end_time,
                         CourseSchedule.location,Section.assignments_enabled,Section.quizzes_enabled,
                         Section.section_name).distinct()
                  .select_from(CourseSchedule)
                  .join(Section,CourseSchedule.section_id==Section.section_id)
                  .join(StudentSection,Section.section_id==StudentSection.section_id)
                  .where(CourseSchedule.course_id.in_(course_ids),
                         StudentSection.student_id==student_id,
                         CourseSchedule.is_deleted.is_(False),
                         Section.is_deleted.is_(False)))
            schedule=_rows(session.execute(stmt).all())
            return schedule
        except ValueError as v:
            logging.warning(f"Error during get crs schdl for enrld sctnn(models): {str(v)}")
            return []
        except Exception as e:
            logging.exception(f"Error during get crs schdl for enrld sctnn(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_student_fee_records(student_id:int):
        session=SessionLocal()
        try:
            stmt = (
                select(
                    StudentFee.student_fees_id.label("student_fees_id"),
                    Program.program_name.label("program"),
                    StudentFee.update_date.label("paid_date"),
                    StudentFee.fee_month.label("month"),
                    StudentFee.fee_amount.label("fee_amount"),
                    StudentFee.voucher_front_pic.label("front_voucher"),
                    StudentFee.voucher_back_pic.label("back_voucher"),
                    func.date(StudentFee.update_date).label("fee_paid_at"),
                    StudentFee.fee_status.label("status"),
                )
                .select_from(StudentFee)
                .join(Program, StudentFee.program_id == Program.program_id)
                .where(
                    StudentFee.student_id == student_id,
                    StudentFee.is_deleted.is_(False),
                )
            )
            # stmt=(select(Program.program_name.label('program'),
            #              StudentFee.update_date.label('paid_date'),
            #              StudentFee.fee_month.label('month'),
            #              StudentFee.fee_amount.label('fee_amount'),
            #              StudentFee.voucher_front_pic.label('front_voucher'),
            #              StudentFee.voucher_back_pic.label('back_voucher'),
            #              func.date(StudentFee.update_date).label('fee_paid_at'),
            #              StudentFee.fee_status.label('status'))
            #       .select_from(StudentFee)
            #       .join(Program,StudentFee.program_id==Program.program_id)
            #       .where(StudentFee.student_id==student_id,StudentFee.is_deleted.is_(False)))
            fee_records=_rows(session.execute(stmt).all())
            if not fee_records:
                logging.warning(f"Fee record not foud for student {student_id}")
                raise ValueError("No record found")

            return fee_records
        except Exception as e:
            logging.exception(f"Error during get stdnt fee record(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def insert_complaint_suggestion(title:str,description:str,user_id:int):
        session=SessionLocal()
        try:
            session.add(ComplaintSuggestion(title=title,description=description,user_id=user_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during insrt complnt status(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_complaint_status(user_id:int):
        session=SessionLocal()
        try:
            stmt=select(ComplaintSuggestion).where(ComplaintSuggestion.user_id==user_id)
            status=_objs(session.execute(stmt).scalars().all())
            if not status:
                raise ValueError("No status fetch")
            return status
        except Exception as e:
            logging.exception(f"Error during get complnt status(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def insert_submission(student_id:int,course_id:int,section_id:int,file_path:str,submission_type:str):
        session=SessionLocal()
        try:
            session.add(StudentSubmission(student_id=student_id,course_id=course_id,
                                          section_id=section_id,file_path=file_path,
                                          submission_type=submission_type))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during insrt submssn(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_all_submissions(student_id:int):
        session=SessionLocal()
        try:
            
            stmt=(select(*StudentSubmission.__table__.columns,Course.course_name)
                  .select_from(StudentSubmission)
                  .join(Course,StudentSubmission.course_id==Course.course_id)
                  .where(StudentSubmission.student_id==student_id)
                  .order_by(StudentSubmission.upload_date.desc()))
            submissions=_rows(session.execute(stmt).all())
            if not submissions:
                raise ValueError("No submissions fetch")
            return submissions
        except Exception as e:
            logging.exception(f"Error during get all submssn(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_student_submission_status(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(StudentSubmission.course_id,StudentSubmission.submission_type,
                         StudentSubmission.marks,StudentSubmission.total_marks)
                  .where(StudentSubmission.student_id==student_id))
            submissions=_rows(session.execute(stmt).all())
            return submissions
        except Exception as e:
            logging.exception(f"Error during get stdnt submssn status(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def upload_fee_voucher(student_id:int,program_id:int,month:str,fee_amount:float,front_path:str,back_path:str):
        session=SessionLocal()
        try:
            session.add(StudentFee(fee_amount=fee_amount,fee_status='due',update_date=func.now(),
                                   voucher_front_pic=front_path,voucher_back_pic=back_path,
                                   program_id=program_id,fee_month=month,student_id=student_id,
                                   is_deleted=False))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during upld fee vchr(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()




    @staticmethod
    def get_student_courses_for_attendance(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(StudentCourse.student_course_id,Course.course_name,Course.credit_hours)
                  .select_from(StudentCourse)
                  .join(Course,StudentCourse.course_id==Course.course_id)
                  .where(StudentCourse.student_id==student_id))
            courses=_rows(session.execute(stmt).all())

            return courses
        except Exception as e:
            logging.exception(f"Error during stdnt course attndnc(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_course_schedule_for_student_course(student_course_id:int):
        session=SessionLocal()
        try:
            stmt=(select(CourseSchedule.course_schedule_id)
                  .select_from(CourseSchedule)
                  .join(StudentCourse,CourseSchedule.course_id==StudentCourse.course_id)
                  .where(StudentCourse.student_course_id==student_course_id))
            schedule=_row(session.execute(stmt).first())
            if not schedule:
                raise ValueError("No schedule found")

            return schedule
        except Exception as e:
            logging.exception(f"Error during cours schdl(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_attendance_summary(student_course_id:int):
        session=SessionLocal()
        try:
            total_lectures_row=_row(session.execute(
                select(func.count().label('total'))
                .select_from(Attendance)
                .where(Attendance.student_course_id==student_course_id)).first())
            attended_row=_row(session.execute(
                select(func.count().label('attended'))
                .select_from(Attendance)
                .where(Attendance.student_course_id==student_course_id,
                       Attendance.attendance_status=='Present')).first())
            return total_lectures_row['total'] if total_lectures_row else 0, \
            attended_row['attended'] if attended_row else 0
        except Exception as e:
            logging.exception(f"Error during attndnc summry(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_attendance_status_details(student_course_id:int):
        session=SessionLocal()
        try:
            stmt=(select(Attendance.attendance_date,Attendance.attendance_status)
                  .where(Attendance.student_course_id==student_course_id)
                  .order_by(Attendance.attendance_date.asc()))
            lecture_status=_rows(session.execute(stmt).all())
            return lecture_status
        except Exception as e:
            logging.exception(f"Error during get attndnc status(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_teacher_name_attendance(student_course_id:int):
        session=SessionLocal()
        try:
            stmt=(select(func.concat(Teacher.first_name,' ',Teacher.last_name).label('teacher_name'))
                  .select_from(TeacherCourse)
                  .join(Teacher,TeacherCourse.teacher_id==Teacher.teacher_id)
                  .join(StudentCourse,StudentCourse.course_id==TeacherCourse.course_id)
                  .where(StudentCourse.student_course_id==student_course_id)
                  .limit(1))
            res=_row(session.execute(stmt).first())
            if not res:
                raise ValueError("No record fetch")

            return res
        except Exception as e:
            logging.exception(f"Error during get tchr name attndnc(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_student_results_with_marks(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(StudentResult.student_semester.label('semester'),Course.course_name,
                         Course.credit_hours,StudentResultMarks.total_marks,
                         StudentResultMarks.student_grade,StudentResultMarks.subject_gpa,
                         StudentResultMarks.status).distinct()
                  .select_from(StudentResult)
                  .join(StudentResultMarks,StudentResult.student_result_id==StudentResultMarks.student_result_id)
                  .join(StudentCourse,StudentResultMarks.student_course_id==StudentCourse.student_course_id)
                  .join(Course,StudentCourse.course_id==Course.course_id)
                  .where(StudentResult.student_id==student_id))
            all_marks=_rows(session.execute(stmt).all())
            return all_marks
        except Exception as e:
            logging.exception(f"Error during get stdn result marks(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_improvement_subjects(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(StudentImprovement.improvement_id.label('id'),StudentImprovement.status,
                         literal('improvement',String).label('type'),Course.course_name,Course.course_id)
                  .select_from(StudentImprovement)
                  .join(Course,StudentImprovement.course_id==Course.course_id)
                  .where(StudentImprovement.student_id==student_id))
            improvements=_rows(session.execute(stmt).all())
            return improvements
        except Exception as e:
            logging.exception(f"Error during get imprvmnt subjs(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_retake_subjects(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(StudentFailSubject.student_fail_id.label('id'),StudentFailSubject.status,
                         literal('retake',String).label('type'),Course.course_name,Course.course_id)
                  .select_from(StudentFailSubject)
                  .join(Course,StudentFailSubject.course_id==Course.course_id)
                  .where(StudentFailSubject.student_id==student_id))
            retakes=_rows(session.execute(stmt).all())
            return retakes
        except Exception as e:
            logging.exception(f"Error during get retake subjs(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_existing_improvement_request(student_id:int):
        session=SessionLocal()
        try:
            stmt=select(StudentImprovement).where(StudentImprovement.student_id==student_id)
            existing=_obj(session.execute(stmt).scalars().first())
            return existing
        except Exception as e:
            logging.exception(f"Error during exstng imprvmnt rqst(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_max_semester_passed(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(func.max(StudentResult.student_semester).label('max_sem'))
                  .where(StudentResult.student_id==student_id))
            res=_row(session.execute(stmt).first())
            return int(res['max_sem']) if res and res['max_sem'] else 0
        except Exception as e:
            logging.exception(f"Error during get mx smrtr pass(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_eligible_improvement_courses(student_id:int,max_semester:int):
        session=SessionLocal()
        try:
            teacher_name=func.group_concat(
                literal_column("DISTINCT CONCAT(teachers.first_name, ' ', teachers.last_name) SEPARATOR ', '")
            ).label('teacher_name')

            stmt=(select(Course.course_id,Course.course_name,Course.credit_hours,
                         teacher_name,func.min(Section.semester).label('semester'))
                  .select_from(Course)
                  .outerjoin(TeacherCourse,and_(Course.course_id==TeacherCourse.course_id,
                                                TeacherCourse.is_deleted.is_(False)))
                  .outerjoin(Teacher,and_(TeacherCourse.teacher_id==Teacher.teacher_id,
                                          Teacher.is_deleted.is_(False)))
                  .outerjoin(Section,and_(Course.course_id==Section.course_id,
                                          Section.is_deleted.is_(False)))
                  .outerjoin(StudentSection,and_(Section.section_id==StudentSection.section_id,
                                                 StudentSection.is_deleted.is_(False)))
                  .outerjoin(StudentCourse,and_(Course.course_id==StudentCourse.course_id,
                                                StudentCourse.is_deleted.is_(False)))
                  .outerjoin(StudentResultMarks,and_(StudentResultMarks.student_course_id==StudentCourse.student_course_id,
                                                     StudentResultMarks.is_deleted.is_(False)))
                  .where(StudentSection.student_id==student_id,
                         StudentCourse.student_id==student_id,
                         Section.semester.between(1,max_semester),
                         or_(StudentResultMarks.student_grade!='F',
                             StudentResultMarks.student_grade.is_(None)),
                         Course.is_deleted.is_(False))
                  .group_by(Course.course_id,Course.course_name,Course.credit_hours)
                  .order_by(text('semester ASC')))
            courses=_rows(session.execute(stmt).all())
            return courses
        except Exception as e:
            logging.exception(f"Error during get elgbl imprvmnt courses(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def delete_improvement_subject(improvement_id:int,student_id:int):
        session=SessionLocal()
        try:
            session.execute(delete(StudentImprovement).where(
                StudentImprovement.improvement_id==improvement_id,
                StudentImprovement.student_id==student_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during dlt imprvmnt subj(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()



    @staticmethod
    def add_improvement_subject(student_id:int,course_id:int):
        session=SessionLocal()
        try:
            session.add(StudentImprovement(student_id=student_id,course_id=course_id,status='Pending'))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during add improvmnt(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()



    @staticmethod
    def add_notification(sender_id:int,sender_role:str,receiver_id:int,receiver_role:str,title:str,description:str,related_course_id:int,status:str):
        session=SessionLocal()
        try:
            session.add(Notification(sender_id=sender_id,sender_role=sender_role,
                                     receiver_id=receiver_id,receiver_role=receiver_role,
                                     title=title,description=description,
                                     related_course_id=related_course_id,status=status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during add notfctns(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()



    @staticmethod
    def get_existing_retake_request(student_id:int):
        session=SessionLocal()
        try:
            stmt=select(StudentFailSubject).where(StudentFailSubject.student_id==student_id)
            existing=_obj(session.execute(stmt).scalars().first())
            return existing
        except Exception as e:
            logging.exception(f"Error during get exstng retake(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_eligible_fail_subjects(student_id:int,max_semester:int):
        session=SessionLocal()
        try:
            teacher_name=func.group_concat(
                literal_column("DISTINCT CONCAT(teachers.first_name, ' ', teachers.last_name) SEPARATOR ', '")
            ).label('teacher_name')

            stmt=(select(Course.course_id,Course.course_name,Course.credit_hours,
                         teacher_name,func.min(Section.semester).label('semester'))
                  .select_from(Course)
                  .outerjoin(TeacherCourse,and_(Course.course_id==TeacherCourse.course_id,
                                                TeacherCourse.is_deleted.is_(False)))
                  .outerjoin(Teacher,and_(TeacherCourse.teacher_id==Teacher.teacher_id,
                                          Teacher.is_deleted.is_(False)))
                  .outerjoin(Section,and_(Course.course_id==Section.course_id,
                                          Section.is_deleted.is_(False)))
                  .outerjoin(StudentSection,and_(Section.section_id==StudentSection.section_id,
                                                 StudentSection.is_deleted.is_(False)))
                  .outerjoin(StudentCourse,and_(Course.course_id==StudentCourse.course_id,
                                                StudentCourse.is_deleted.is_(False)))
                  .outerjoin(StudentResultMarks,and_(StudentResultMarks.student_course_id==StudentCourse.student_course_id,
                                                     StudentResultMarks.is_deleted.is_(False)))
                  .where(StudentSection.student_id==student_id,
                         StudentCourse.student_id==student_id,
                         Section.semester.between(1,max_semester),
                         StudentResultMarks.student_grade=='F',
                         Course.is_deleted.is_(False))
                  .group_by(Course.course_id,Course.course_name,Course.credit_hours)
                  .order_by(text('semester ASC')))
            courses=_rows(session.execute(stmt).all())
            return courses
        except Exception as e:
            logging.exception(f"Error during get elgbl fail subjs(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def add_fail_subject(student_id:int,course_id:int):
        session=SessionLocal()
        try:
            session.add(StudentFailSubject(student_id=student_id,course_id=course_id,status='Pending'))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during add fail subj(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def delete_fail_subject(fail_id:int,student_id:int):
        session=SessionLocal()
        try:
            session.execute(delete(StudentFailSubject).where(
                StudentFailSubject.student_fail_id==fail_id,
                StudentFailSubject.student_id==student_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during dlt fail subj(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_active_semester_freeze_request(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(SemesterFreezeStudent)
                  .where(SemesterFreezeStudent.student_id==student_id)
                  .order_by(SemesterFreezeStudent.applied_date.desc())
                  .limit(1))
            request=_obj(session.execute(stmt).scalars().first())
            return request
        except Exception as e:
            logging.exception(f"Error during get active smstr frz rqst(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_last_recorded_semester(student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(StudentResultMarks.student_semester)
                  .select_from(StudentResultMarks)
                  .join(StudentCourse,StudentResultMarks.student_course_id==StudentCourse.student_course_id)
                  .where(StudentCourse.student_id==student_id)
                  .order_by(StudentResultMarks.student_result_id.desc())
                  .limit(1))
            result=_row(session.execute(stmt).first())
            return result['student_semester'] if result else None
        except Exception as e:
            logging.exception(f"Error during get last recorded smstr(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def add_semester_freeze_request(student_id:int,semester:int,reason:str):
        session=SessionLocal()
        try:
            session.add(SemesterFreezeStudent(student_id=student_id,semester=semester,
                                              reason=reason,status='Pending'))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during add smstr freeze rqst(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_eligible_summer_failed_subjects(student_id:int):
        session=SessionLocal()
        try:
            rm2=aliased(StudentResultMarks)
            sc2=aliased(StudentCourse)
            max_failed_semester=(select(func.max(rm2.student_semester))
                                 .select_from(rm2)
                                 .join(sc2,rm2.student_course_id==sc2.student_course_id)
                                 .where(sc2.student_id==student_id,rm2.student_grade=='F')
                                 .scalar_subquery())

            stmt=(select(Course.course_id,Course.course_name,Course.credit_hours,
                         StudentResultMarks.student_semester.label('semester'),
                         func.concat(Teacher.first_name,' ',Teacher.last_name).label('teacher_name'))
                  .select_from(StudentResultMarks)
                  .join(StudentCourse,StudentResultMarks.student_course_id==StudentCourse.student_course_id)
                  .join(Course,StudentCourse.course_id==Course.course_id)
                  .outerjoin(TeacherCourse,Course.course_id==TeacherCourse.course_id)
                  .outerjoin(Teacher,TeacherCourse.teacher_id==Teacher.teacher_id)
                  .where(StudentCourse.student_id==student_id,
                         StudentResultMarks.student_grade=='F',
                         StudentResultMarks.student_semester==max_failed_semester))
            failed_subjects=_rows(session.execute(stmt).all())
            return failed_subjects
        except Exception as e:
            logging.exception(f"Error during get elgbl summer fail subj(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_latest_summer_semester():
        session=SessionLocal()
        try:
            stmt=(select(SummerSemester)
                  .where(SummerSemester.is_deleted.is_(False),SummerSemester.status=='open')
                  .order_by(SummerSemester.summer_semesters_id.desc())
                  .limit(1))
            semester=_obj(session.execute(stmt).scalars().first())
            return semester
        except Exception as e:
            logging.exception(f"Error during get latest summr smstr(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_failed_subjects_for_last_semester(student_id:int,last_semester:int):
        session=SessionLocal()
        try:
            stmt=(select(Course.course_id,Course.course_name,Course.credit_hours,
                         func.concat(Teacher.first_name,' ',Teacher.last_name).label('teacher_name'),
                         StudentResultMarks.student_semester.label('semester'))
                  .select_from(StudentResultMarks)
                  .join(StudentCourse,StudentResultMarks.student_course_id==StudentCourse.student_course_id)
                  .join(Course,StudentCourse.course_id==Course.course_id)
                  .outerjoin(TeacherCourse,TeacherCourse.course_id==Course.course_id)
                  .outerjoin(Teacher,TeacherCourse.teacher_id==Teacher.teacher_id)
                  .where(StudentCourse.student_id==student_id,
                         StudentResultMarks.student_semester==last_semester,
                         StudentResultMarks.status=='Fail'))
            subjects=_rows(session.execute(stmt).all())
            return subjects
        except Exception as e:
            logging.exception(f"Error during get fail subjs(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_system_setting(key:str):
        session=SessionLocal()
        try:
            stmt=select(SystemSetting.setting_value).where(SystemSetting.setting_key==key)
            result=_row(session.execute(stmt).first())
            return result['setting_value'] if result else None
        except Exception as e:
            logging.exception(f"Error during system setting(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def add_summer_subject(student_id:int,course_id:int,summer_semester_id:int):
        session=SessionLocal()
        try:
            existing=session.execute(
                select(SummerRegistration).where(
                    SummerRegistration.student_id==student_id,
                    SummerRegistration.course_id==course_id,
                    SummerRegistration.summer_semesters_id==summer_semester_id)).scalars().first()
            if existing:
                return False

            session.add(SummerRegistration(student_id=student_id,course_id=course_id,
                                           summer_semesters_id=summer_semester_id,
                                           registration_date=func.now()))
            session.commit()
            return True
        except Exception as e:
            logging.exception(f"Error during add summer subj(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def delete_summer_subject(student_id:int,course_id:int,summer_semester_id:int):
        session=SessionLocal()
        try:
            session.execute(delete(SummerRegistration).where(
                SummerRegistration.student_id==student_id,
                SummerRegistration.course_id==course_id,
                SummerRegistration.summer_semesters_id==summer_semester_id))
            session.commit()
            return True
        except Exception as e:
            logging.exception(f"Error during dlt summer subj(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_selected_summer_subjects(student_id:int,summer_semester_id:int):
        session=SessionLocal()
        try:
            stmt=(select(SummerRegistration.course_id,Course.course_name,Course.credit_hours,
                         literal('Summer',String).label('type'),
                         literal('Registered',String).label('status'))
                  .select_from(SummerRegistration)
                  .join(Course,SummerRegistration.course_id==Course.course_id)
                  .where(SummerRegistration.student_id==student_id,
                         SummerRegistration.summer_semesters_id==summer_semester_id))
            selected=_rows(session.execute(stmt).all())
            return selected
        except Exception as e:
            logging.exception(f"Error during slsct summer smstr subj(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def create_notification(sender_id:int,sender_role:str,receiver_role:str,title:str,description:str,related_course_id:int,status:str,receiver_id:int):
        session=SessionLocal()
        try:
            status='Pending'
            if receiver_id:
                session.add(Notification(sender_id=sender_id,sender_role=sender_role,
                                         receiver_id=receiver_id,receiver_role=receiver_role,
                                         title=title,description=description,
                                         related_course_id=related_course_id,status=status))
            else:
                session.add(Notification(sender_id=sender_id,sender_role=sender_role,
                                         receiver_role=receiver_role,title=title,
                                         description=description,
                                         related_course_id=related_course_id,status=status))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during create notification(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_all_teachers():
        session=SessionLocal()
        try:
            stmt=select(Teacher.teacher_id,Teacher.first_name,Teacher.last_name).where(Teacher.is_deleted.is_(False))
            teachers=_rows(session.execute(stmt).all())
            return teachers
        except Exception as e:
            logging.exception(f"Error during get all teachers(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def get_fyp_by_id_and_student(fyp_id:int,student_id:int):
        session=SessionLocal()
        try:
            stmt=select(FypGroup.fyp_id).where(FypGroup.fyp_id==fyp_id,FypGroup.student_id==student_id)
            fyp=_row(session.execute(stmt).first())
            return fyp
        except Exception as e:
            logging.exception(f"Error during fyp id and student(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_current_semester(student_id:int):
        session=SessionLocal()
        try:
            stmt=select(Student.current_semester).where(Student.student_id==student_id,Student.is_deleted.is_(False))
            res=_row(session.execute(stmt).first())
            if not res:
                return None

            current_smstr=res['current_semester']
            return current_smstr
        except Exception as e:
            logging.exception(f"Error during get current smstr(models): {str(e)}")
            raise
        finally:
            session.close()






    @staticmethod
    def get_fyp_project(student_id:int):
        session=SessionLocal()
        try:
            
            stmt=(select(*FypGroup.__table__.columns,
                         Teacher.first_name.label('t_fname'),
                         Teacher.last_name.label('t_lname'))
                  .select_from(FypGroup)
                  .outerjoin(Teacher,FypGroup.teacher_id==Teacher.teacher_id)
                  .where(FypGroup.student_id==student_id))
            fyp=_row(session.execute(stmt).first())
            return fyp
        except Exception as e:
            logging.exception(f"Error during get fyp project(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def insert_fyp_proposal(student_id:int,title:str,description:str,teacher_id:int,filename:str):
        session=SessionLocal()
        try:
            session.add(FypGroup(project_title=title,description=description,teacher_id=teacher_id,
                                 student_id=student_id,status='In Progress',progress=0,
                                 last_submission=filename))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during insert fyp proposal(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()



    @staticmethod
    def get_fyp_messages(fyp_id:int):
        session=SessionLocal()
        try:
            stmt=(select(FypMessage)
                  .where(FypMessage.fyp_id==fyp_id)
                  .order_by(FypMessage.created_at.asc()))
            messages=_objs(session.execute(stmt).scalars().all())
            return messages
        except Exception as e:
            logging.exception(f"Error during get fyp message(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def insert_fyp_message(fyp_id:int,student_id:int,role:str,message_text:str):
        session=SessionLocal()
        try:
            group=_row(session.execute(
                select(FypGroup.teacher_id).where(FypGroup.fyp_id==fyp_id)).first())
            if group:
                teacher_id=group['teacher_id']
                session.add(FypMessage(fyp_id=fyp_id,teacher_id=teacher_id,student_id=student_id,
                                       sender_role=role,message=message_text))
                session.commit()
        except Exception as e:
            logging.exception(f"Error during insert fyp message(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()



    @staticmethod
    def update_fyp_data(student_id:int,title:str,filename:str=None):
        session=SessionLocal()
        try:
            if filename:
                result=_row(session.execute(
                    select(FypGroup.progress).where(FypGroup.student_id==student_id)).first())
                if not result:
                    logging.warning(f"Student {student_id} not fyp found")
                    raise ValueError("FYP Not found")

                new_progress=min((result['progress'] or 0)+10,100)
                session.execute(update(FypGroup)
                                .where(FypGroup.student_id==student_id)
                                .values(project_title=title,last_submission=filename,progress=new_progress))
                session.commit()
            else:
                session.execute(update(FypGroup)
                                .where(FypGroup.student_id==student_id)
                                .values(project_title=title))
                session.commit()
        except Exception as e:
            logging.exception(f"Error during update fyp(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()



    @staticmethod
    def get_teacher_full_details(teacher_id:int):
        session=SessionLocal()
        try:
            stmt=(select(Teacher.teacher_id,Teacher.first_name,Teacher.last_name,
                         Teacher.email,Teacher.contact_num)
                  .where(Teacher.teacher_id==teacher_id))
            teacher=_row(session.execute(stmt).first())
            return teacher
        except Exception as e:
            logging.exception(f"Error during get teacher full details(models): {str(e)}")
            raise
        finally:
            session.close()



class NotificationModel:
    @staticmethod
    def get_notifications_for_user(user_id:int,student_id:int):
        session=SessionLocal()
        try:
            stmt=(select(Notification)
                  .where(or_(Notification.sender_id==user_id,
                             and_(Notification.receiver_role=='student',
                                  Notification.receiver_id==student_id)))
                  .order_by(Notification.created_at.desc()))
            notifications=_objs(session.execute(stmt).scalars().all())
            return notifications
        except Exception as e:
            logging.exception(f"Error during get notification(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_active_notifications(user_id:int,role:str):
        session=SessionLocal()
        try:
            stmt=(select(Notification.id,Notification.title,Notification.description,Notification.created_at)
                  .where(or_(Notification.receiver_id==user_id,Notification.receiver_id.is_(None)),
                         Notification.receiver_role==role,
                         Notification.is_deleted.is_(False),
                         Notification.status=='Pending'))
            notifications=_rows(session.execute(stmt).all())
            return notifications
        except Exception as e:
            logging.exception(f"Error during active notification(models): {str(e)}")
            raise
        finally:
            session.close()