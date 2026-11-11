import logging
from datetime import datetime, time, timedelta

from sqlalchemy import select, update, func, and_, or_, text, distinct, literal_column,case
from sqlalchemy.dialects.mysql import insert as mysql_insert

from db.session import SessionLocal
from core.exceptions import NotFoundError
from db.models.orm import (  
    User, Student, Program, Course, StudentCourse, TeacherCourse, Teacher,
    CourseSchedule, Section, StudentSection, ComplaintSuggestion,
    StudentSubmission, Attendance, StudentResult, StudentResultMarks,
    Notification, FypGroup, FypMessage, CourseAttendanceLog
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


class TeacherModel:
    @staticmethod
    def get_profile(teacher_id:int):
        session=SessionLocal()
        try:
            stmt=select(Teacher).where(Teacher.teacher_id==teacher_id,Teacher.is_deleted.is_(False))
            result=_obj(session.execute(stmt).scalars().first())
            return result
        except Exception as e:
            logging.exception(f"Error during get profile teacher(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_by_email(email:str):
        session=SessionLocal()
        try:
            stmt=select(User).where(User.email==email,User.is_deleted.is_(False))
            user=_obj(session.execute(stmt).scalars().first())
            return user
        except Exception as e:
            logging.exception(f"Error during get by email(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_email_by_user_id(user_id:int):
        session=SessionLocal()
        try:
            stmt=select(User.email).where(User.user_id==user_id,User.is_deleted.is_(False))
            row=_row(session.execute(stmt).first())
            return row['email'] if row else None
        except Exception as e:
            logging.exception(f"Error during get email by user id(models): {str(e)}")
            return None
        finally:
            session.close()


    @staticmethod
    def get_by_user_id(user_id:int):
        session=SessionLocal()
        try:
            stmt=select(Teacher).where(Teacher.user_id==user_id,Teacher.is_deleted.is_(False))
            teacher=_obj(session.execute(stmt).scalars().first())
            return teacher
        except Exception as e:
            logging.exception(f"Error furing user by id(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_full_schedule(teacher_id:int):
        session=SessionLocal()
        try:
            stmt=(select(TeacherCourse.teacher_course_id,
                         Program.program_coordinator.label('coordinator_name'),
                         Program.program_name.label('class_name'),
                         Course.course_id,Course.course_name,
                         Section.semester,Section.section_id,
                         Section.section_name.label('section'),
                         CourseSchedule.day_of_week,
                         CourseSchedule.start_time.label('start'),
                         CourseSchedule.end_time.label('end'))
                  .select_from(TeacherCourse)
                  .join(Course,TeacherCourse.course_id==Course.course_id)
                  .join(Program,Course.program_id==Program.program_id)
                  .join(Section,Course.course_id==Section.course_id)
                  .join(CourseSchedule,Section.section_id==CourseSchedule.section_id)
                  .where(TeacherCourse.teacher_id==teacher_id)
                  .order_by(func.field(CourseSchedule.day_of_week,'Monday','Tuesday','Wednesday','Thursday','Friday'),
                            CourseSchedule.start_time))
            result=_rows(session.execute(stmt).all())
            return result
        except Exception as e:
            logging.exception(f"Error during full schdl(models): {str(e)}")
        finally:
            session.close()


    @staticmethod
    def get_class_structure(section_id:int):
        session=SessionLocal()
        try:
            total_enroll=(select(func.count()).select_from(StudentSection)
                          .where(StudentSection.section_id==Section.section_id)
                          .correlate(Section).scalar_subquery().label('total_enroll'))

            stmt=(select(Course.course_id.label('class_id'),Program.program_coordinator,
                         Program.program_name,Section.semester,Course.course_name,
                         Section.section_name,Section.section_id,
                         Section.assignments_enabled,Section.quizzes_enabled,
                         total_enroll)
                  .select_from(Section)
                  .join(Course,Section.course_id==Course.course_id)
                  .join(Program,Course.program_id==Program.program_id)
                  .where(Section.section_id==section_id))
            result=_rows(session.execute(stmt).all())
            return result
        except Exception as e:
            logging.exception(f"Error during class strctr(models): {str(e)}")
        finally:
            session.close()


    @staticmethod
    def toggle_upload_status(section_id:int,upload_type:str):
        session=SessionLocal()
        try:
            column="assignments_enabled" if upload_type == 'assignment' else "quizzes_enabled"
            session.execute(update(Section)
                            .where(Section.section_id==section_id)
                            .values({column:literal_column(f"1 - {column}")}))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during toggle(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_attendance_meta(section_id:int):
        session=SessionLocal()
        try:
            stmt=(select(Course.course_name,Course.course_id,CourseSchedule.course_schedule_id,
                         Section.section_id,Section.semester,Section.section_name,
                         CourseSchedule.end_time,CourseSchedule.day_of_week)
                  .select_from(Section)
                  .join(Course,Section.course_id==Course.course_id)
                  .join(CourseSchedule,Section.section_id==CourseSchedule.section_id)
                  .where(Section.section_id==section_id)
                  .limit(1))
            result=_row(session.execute(stmt).first())
            return result
        except Exception as e:
            logging.exception(f"Error during attndnc meta(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_lecture_no(course_schedule_id:int):
        session=SessionLocal()
        try:
            stmt=(select(func.count(distinct(CourseAttendanceLog.attendance_date)).label('total_lectures'))
                  .where(CourseAttendanceLog.course_schedule_id==course_schedule_id))
            res=_row(session.execute(stmt).first())
            return res
        except Exception as e:
            logging.exception(f"Error during lec no(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def check_attendance_marked(schedule_id:int,attendance_date:datetime):
        session=SessionLocal()
        try:
            stmt=(select(func.count().label('count'))
                  .select_from(Attendance)
                  .where(Attendance.course_schedule_id==schedule_id,
                         Attendance.attendance_date==attendance_date))
            count=_row(session.execute(stmt).first())['count']
            return count > 0
        except Exception as e:
            logging.exception(f"Error during chk attndc mark(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_student_list_for_attendance(section_id:int,course_id:int):
        session=SessionLocal()
        try:
            stmt=(select(StudentSection.student_id,
                         func.concat(Student.first_name,' ',Student.last_name).label('student_name'),
                         StudentCourse.student_course_id)
                  .select_from(StudentSection)
                  .join(StudentCourse,StudentSection.student_id==StudentCourse.student_id)
                  .join(Student,StudentSection.student_id==Student.student_id)
                  .where(StudentSection.section_id==section_id,StudentCourse.course_id==course_id))
            result=_rows(session.execute(stmt).all())
            return result
        except Exception as e:
            logging.exception(f"Error during stndt lst attndc(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def save_bulk_attendance(attendance_data:str):
        session=SessionLocal()
        try:
            keys=("student_course_id","course_schedule_id","attendance_date","attendance_status","student_id")
            rows=[dict(zip(keys,row)) for row in attendance_data]

            stmt=mysql_insert(Attendance)
            stmt=stmt.on_duplicate_key_update(attendance_status=stmt.inserted.attendance_status)
            session.execute(stmt,rows)
            session.commit()
        except Exception as e:
            logging.exception(f"Error during sv blk attndc(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def save_course_attendance_log(teacher_id:int,course_id:int,course_schedule_id:int,attendance_date:datetime,semester:int,attendance_data:str):
        session=SessionLocal()
        try:
            total_students=len(attendance_data)
            total_present =sum(1 for row in attendance_data if row[3] == 'Present')
            total_absent=total_students - total_present

            existing=_row(session.execute(
                select(CourseAttendanceLog.log_id)
                .where(CourseAttendanceLog.course_schedule_id==course_schedule_id,
                       CourseAttendanceLog.attendance_date==attendance_date)).first())

            if existing:
                session.execute(update(CourseAttendanceLog)
                                .where(CourseAttendanceLog.log_id==existing['log_id'])
                                .values(total_students=total_students,total_present=total_present,
                                        total_absent=total_absent))
            else:
                session.add(CourseAttendanceLog(teacher_id=teacher_id,course_id=course_id,
                                                course_schedule_id=course_schedule_id,
                                                attendance_date=attendance_date,semester=semester,
                                                total_students=total_students,
                                                total_present=total_present,
                                                total_absent=total_absent))

            session.commit()
        except Exception as e:
            logging.exception(f"Error during save crs attndc(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_fyp_groups(teacher_id:int):
        session=SessionLocal()
        try:
            stmt=(select(*FypGroup.__table__.columns,
                         Student.first_name,Student.last_name,
                         Student.student_id.label('reg_num'),
                         Student.contact,Student.email,
                         Program.program_name,
                         func.any_value(Section.semester).label('semester'))
                  .select_from(FypGroup)
                  .join(Student,FypGroup.student_id==Student.student_id)
                  .outerjoin(Program,Student.program_id==Program.program_id)
                  .outerjoin(StudentSection,Student.student_id==StudentSection.student_id)
                  .outerjoin(Section,StudentSection.section_id==Section.section_id)
                  .where(FypGroup.teacher_id==teacher_id)
                  .group_by(FypGroup.fyp_id))
            groups=_rows(session.execute(stmt).all())
            for group in groups:
                msg_stmt=(select(FypMessage)
                          .where(FypMessage.fyp_id==group['fyp_id'])
                          .order_by(FypMessage.created_at.asc()))
                group['messages']=_objs(session.execute(msg_stmt).scalars().all())

            return groups
        except Exception as e:
            logging.exception(f"Error during fyp grps(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def update_fyp_status(fyp_id:int,status:str,teacher_id:int):
        session=SessionLocal()
        try:
            result=session.execute(update(FypGroup)
                                   .where(FypGroup.fyp_id==fyp_id,FypGroup.teacher_id==teacher_id)
                                   .values(status=status))
            if result.rowcount==0:
                raise NotFoundError("FYP not found")

            session.commit()
        except Exception as e:
            logging.exception(f"Error during updt fyp(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def add_fyp_message(fyp_id:int,teacher_id:int,message_text:str):
        session=SessionLocal()
        try:
            res=_row(session.execute(
                select(FypGroup.student_id).where(FypGroup.fyp_id==fyp_id)).first())
            if res:
                session.add(FypMessage(fyp_id=fyp_id,teacher_id=teacher_id,
                                       student_id=res['student_id'],
                                       sender_role='teacher',message=message_text))
                session.commit()
        except Exception as e:
            logging.exception(f"Error during add fyp msg(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def update_submission_marks(sub_id:int,marks:int,section_id:int,total:int,sub_type:str):
        session=SessionLocal()
        try:
            result=session.execute(update(StudentSubmission)
                            .where(StudentSubmission.submission_id==sub_id,
                                   StudentSubmission.section_id==section_id,
                                   StudentSubmission.submission_type==sub_type,
                                   StudentSubmission.is_deleted.is_(False))
                            .values(marks=marks,total_marks=total))
            if result.rowcount==0:
                raise NotFoundError("Submission not found for this section and type")
            
            session.commit()
        except Exception as e:
            logging.exception(f"Error during updt submssn(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_submissions_by_type(section_id:int,sub_type:str):
        session=SessionLocal()
        try:
            stmt=(select(StudentSubmission.submission_id,StudentSubmission.student_id,
                         StudentSubmission.file_path,StudentSubmission.upload_date,
                         StudentSubmission.marks,StudentSubmission.total_marks,
                         StudentSubmission.submission_status,
                         Student.first_name,Student.last_name)
                  .select_from(StudentSubmission)
                  .join(Student,StudentSubmission.student_id==Student.student_id)
                  .where(StudentSubmission.section_id==section_id,
                         func.lower(StudentSubmission.submission_type)==func.lower(sub_type)))
            subs=_rows(session.execute(stmt).all())

            meta_stmt=(select(Course.course_name,Section.section_name)
                       .select_from(Section)
                       .join(Course,Section.course_id==Course.course_id)
                       .where(Section.section_id==section_id))
            meta=_row(session.execute(meta_stmt).first())
            return subs,meta
        except Exception as e:
            logging.exception(f"Error during submsn type(models): {str(e)}")
            raise
        finally:
            session.close()


    @staticmethod
    def get_grading_data(course_id:int,section_id:int):
        session=SessionLocal()
        try:
            stmt=(select(Student.student_id,Student.first_name,Student.last_name,
                         StudentResultMarks.marks_id.label('has_result'),
                         StudentResultMarks.student_grade,StudentResultMarks.total_marks)
                  .select_from(Student)
                  .join(StudentSection,Student.student_id==StudentSection.student_id)
                  .join(StudentCourse,and_(Student.student_id==StudentCourse.student_id,
                                           StudentCourse.course_id==course_id))
                  .outerjoin(StudentResultMarks,StudentCourse.student_course_id==StudentResultMarks.student_course_id)
                  .where(StudentSection.section_id==section_id))
            res=_rows(session.execute(stmt).all())
            return res
        except Exception as e:
            logging.exception(f"Error during grading data(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def is_section_owned_by_teacher(section_id:int,teacher_id:int)->bool:
        session=SessionLocal()
        try:
            stmt=(select(TeacherCourse.teacher_course_id)
                .select_from(TeacherCourse)
                .join(Section,TeacherCourse.course_id==Section.course_id)
                .where(Section.section_id==section_id,
                TeacherCourse.teacher_id==teacher_id,
                TeacherCourse.is_deleted.is_(False),))
            return session.execute(stmt).first() is not None
        except Exception as e:
            logging.exception(f"Error during is sct owned(models): {str(e)}")
            raise
        finally:
            session.close()



    @staticmethod
    def process_student_result(sid:int,section_id:int,course_id: int,semester:int,data: dict):
        session=SessionLocal()
        try:
            sc_record=_row(session.execute(
                select(StudentCourse.student_course_id)
                .where(
                    StudentCourse.student_id==sid,
                    StudentCourse.course_id==course_id,
                    StudentCourse.is_deleted.is_(False),)).first())

            if not sc_record:
                raise NotFoundError("Student course enrollment not found")

            res_parent=_row(session.execute(
                select(StudentResult.student_result_id)
                .where(
                    StudentResult.student_id==sid,
                    StudentResult.student_semester==semester,)).first())

            if res_parent:
                res_id=res_parent["student_result_id"]
            else:
                new_result=StudentResult(
                    student_id=sid,
                    student_semester=semester,
                    result_status=data["status"],
                    overall_gpa=data["gpa"],)
                session.add(new_result)
                session.flush()
                res_id=new_result.student_result_id

            stmt=mysql_insert(StudentResultMarks).values(
                student_course_id=sc_record["student_course_id"],
                student_result_id=res_id,
                total_marks=data["total"],
                student_grade=data["grade"],
                status=data["status"],
                student_semester=semester,
                sessional_marks=data["sessional"],
                mid_marks=data["mids"],
                final_marks=data["final"],
                subject_gpa=data["gpa"],
            )
            stmt=stmt.on_duplicate_key_update(
                total_marks=data["total"],
                student_grade=data["grade"],
                status=data["status"],
                sessional_marks=data["sessional"],
                mid_marks=data["mids"],
                final_marks=data["final"],
                subject_gpa=data["gpa"],
            )
            session.execute(stmt)

            # Recalculate the semester GPA as a credit-hour-weighted average.
            # If course credit hours are missing or zero, fall back to a
            # regular average of the subject GPAs.
            aggregate=_row(session.execute(select(func.coalesce(
                        func.sum(
                            StudentResultMarks.subject_gpa
                            * func.coalesce(Course.credit_hours, 0)
                        )
                        / func.nullif(
                            func.sum(func.coalesce(Course.credit_hours, 0)), 0
                        ),
                        func.avg(StudentResultMarks.subject_gpa),
                    ).label("overall_gpa"),
                    func.sum(
                        case(
                            (StudentResultMarks.status=="Fail", 1),
                            else_=0,
                        )
                    ).label("failed_count"),
                )
                .select_from(StudentResultMarks)
                .join(
                    StudentCourse,
                    StudentResultMarks.student_course_id
                    == StudentCourse.student_course_id,
                )
                .join(Course, StudentCourse.course_id == Course.course_id)
                .where(
                    StudentResultMarks.student_result_id == res_id,
                    StudentResultMarks.is_deleted.is_(False),
                )
            ).first())

            session.execute(
                update(StudentResult)
                .where(StudentResult.student_result_id == res_id)
                .values(
                    overall_gpa=round(float(aggregate["overall_gpa"] or 0), 2),
                    result_status=(
                        "Fail" if aggregate["failed_count"] else "Pass"
                    ),
                )
            )

            session.commit()
        except Exception as e:
            session.rollback()
            logging.exception(
                f"Error during processing student result: {str(e)}"
            )
            raise
        finally:
            session.close()

    # @staticmethod
    # def process_student_result(sid:int,section_id:int,course_id:int,semester:int,data:str):
    #     session=SessionLocal()
    #     try:
    #         sc_record=_row(session.execute(
    #             select(StudentCourse.student_course_id)
    #             .where(StudentCourse.student_id==sid,StudentCourse.course_id==course_id)).first())
    #         if not sc_record:
    #             logging.error(f"Error during stnd crs id(models) for student id: {sid}")
    #             return

    #         res_parent=_row(session.execute(
    #             select(StudentResult.student_result_id)
    #             .where(StudentResult.student_id==sid,
    #                    StudentResult.student_semester==semester)).first())
    #         res_id=res_parent['student_result_id'] if res_parent else None

    #         if not res_id:
    #             new_result=StudentResult(student_id=sid,student_semester=semester,
    #                                      result_status=data['status'],overall_gpa=data['gpa'])
    #             session.add(new_result)
    #             session.flush()
    #             res_id=new_result.student_result_id


    #         stmt=mysql_insert(StudentResultMarks).values(
    #             student_course_id=sc_record['student_course_id'],student_result_id=res_id,
    #             total_marks=data['total'],student_grade=data['grade'],status=data['status'],
    #             student_semester=semester,sessional_marks=data['sessional'],
    #             mid_marks=data['mids'],final_marks=data['final'],subject_gpa=data['gpa'])
    #         stmt=stmt.on_duplicate_key_update(
    #             total_marks=data['total'],student_grade=data['grade'],status=data['status'],
    #             sessional_marks=data['sessional'],mid_marks=data['mids'],
    #             final_marks=data['final'],subject_gpa=data['gpa'])
    #         session.execute(stmt)
    #         session.commit()
    #     except Exception as e:
    #         logging.exception(f"Error during prcs stnd res(models): {str(e)}")
    #         session.rollback()
    #         raise
    #     finally:
    #         session.close()


    @staticmethod
    def insert_complaint_suggestion(title:str,description:str,user_id:int):
        session=SessionLocal()
        try:
            session.add(ComplaintSuggestion(title=title,description=description,user_id=user_id))
            session.commit()
        except Exception as e:
            logging.exception(f"Error during inst complnt suggst(models): {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()




class Notifications:

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
            logging.exception(f"Error during actv notf(models): {str(e)}")
            raise
        finally:
            session.close()



