import os
import bleach
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta
from utils.exceptions import *
from werkzeug.security import check_password_hash
from teachers_module.teachers_models import *
import logging





class TeacherService:


    @staticmethod
    def _format_time(time_obj):
        if isinstance(time_obj,timedelta):
            return (datetime.min + time_obj).time().strftime('%I:%M:5p')
        return time_obj


    @staticmethod
    def authenticate_teacher(email:str,password:str):
        try:
            user=TeacherModel.get_by_email(email)
            if not user or user['role_id'] !=1 or not check_password_hash(user['password'],password):
                logging.warning(f"Invalid credentials: {email}")
                raise BusinessRuleError("Invalid Credentials")

            user_id=user['user_id']
            teacher_obj=TeacherModel.get_by_user_id(user_id)
            if not teacher_obj:
                logging.error(f"Teacher record not found id: {user_id}")
                raise NotFoundError("Record Not found")

            return user,teacher_obj
        except (BusinessRuleError,NotFoundError) :
            raise
        except Exception as e:
            logging.exception(f"Error during authnct tchr service: {str(e)}")
            raise


    @staticmethod
    def teacher_dashboard(user_id:int,teacher_id:int):
        try:
            today=datetime.now().strftime('%A')
            full_schedule=TeacherModel.get_full_schedule(teacher_id)
            if not full_schedule:
                return {
                    "access_denied":True,
                    "message":"No schedule found"
                }

            for row in full_schedule:
                row['start']=TeacherService._format_time(row.get('start'))
                row['end']=TeacherService._format_time(row.get('end'))

            active_notifications=Notifications.get_active_notifications(user_id,'teacher')
            today_list=[row for row in full_schedule if row['day_of_week']==today]
            return {
                "access_denied":False,
                "full_schedule":full_schedule,
                "active_notifications":active_notifications,
                "today_name":today,
                "today_list":today_list
            }
        except Exception as e:
            logging.exception(f"Error during tchr dashbd service: {str(e)}")
            raise


    @staticmethod
    def class_attendance(teacher_id:int):
        try:
            today=datetime.now().strftime('%A')
            full_schedule=TeacherModel.get_full_schedule(teacher_id)
            if not full_schedule:
                return {
                    "access_denied":True,
                    "message":"No record found"
                }        

            for row in full_schedule:
                row['start']=TeacherService._format_time(row.get('start'))
                row['end']=TeacherService._format_time(row.get('end'))

            today_list=[row for row in full_schedule if row['day_of_week']==today]
            return {
                "access_denied":False,
                "today_name":today,
                "full_schedule":full_schedule,
                "today_schedule":today_list
            }
        except (NotFoundError) as b:
            logging.error(f"Schedule record not found tchr id: {teacher_id} as: {str(b)}")
            raise
        except Exception as e:
            logging.exception(f"Error during clss attndc serv: {str(e)}")
            raise



    @staticmethod
    def get_class_details(teacher_id:int,section_id:int):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id,teacher_id):
                logging.warning(f"Teacher id {teacher_id} try to access unauthorized section id {section_id}")
                raise BusinessRuleError("Unauthorized access")

            structure=TeacherModel.get_class_structure(section_id)
            if not structure:
                raise NotFoundError("No class found")

            return structure
        except (BusinessRuleError,NotFoundError):
            raise
        except Exception as e:
            logging.exception(f"Error during cls strct service: {str(e)}")
            raise


    @staticmethod
    def toggle_upload_status(teacher_id:int,section_id:int,upload_type:str):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id,teacher_id):
                raise BusinessRuleError("Unauthorized access to this section")
            
            if upload_type not in ['assignment','quiz']:
                raise ValidationError("Invalid upload type")
                
            TeacherModel.toggle_upload_status(section_id,upload_type)
        except (BusinessRuleError,ValidationError):
            raise
        except Exception as e:
            logging.exception(f"Error during toggle upld stus service: {str(e)}")
            raise


    @staticmethod
    def prepare_attendance_data(teacher_id:int,section_id:int):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id,teacher_id):
                raise BusinessRuleError("Unauthorized access to mark attendance")

            meta=TeacherModel.get_attendance_meta(section_id)
            if not meta:
                raise NotFoundError("Attendance metadata not found")

            students=TeacherModel.get_student_list_for_attendance(section_id, meta['course_id'])
            lecture_info=TeacherModel.get_lecture_no(meta['course_schedule_id'])
            lecture_no=(lecture_info['total_lectures'] or 0) + 1
            today=datetime.now().strftime('%A')
            today_date=datetime.now().strftime('%Y-%m-%d')
            already_marked=TeacherModel.check_attendance_marked(meta['course_schedule_id'],today_date)

            return{
                "course_name":meta['course_name'],
                "meta": meta,
                "students":students,
                "lecture_no":lecture_no,
                "today":today,
                "attendance_date":today_date,
                "already_marked":already_marked
            }
        except (BusinessRuleError,NotFoundError):
            raise
        except Exception as e:
            logging.exception(f"Error during prpar atndnc service: {str(e)}")
            raise


    @staticmethod
    def submit_attendance(teacher_id:int,section_id:int,date_str:str,form_data:dict):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id,teacher_id):
                raise BusinessRuleError("Unauthorized access")

            meta=TeacherModel.get_attendance_meta(section_id)
            sched_id=meta['course_schedule_id']
            course_id=meta['course_id']
            semester=meta['semester']
            
            try:
                att_date=datetime.strptime(date_str,'%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Invalid date format")

            if TeacherModel.check_attendance_marked(sched_id,att_date):
                raise BusinessRuleError("Attendance is already marked for this date.")

            students=TeacherModel.get_student_list_for_attendance(section_id,course_id)
            bulk_data=[]
            
            for st in students:
                sc_id=st['student_course_id']
                sid=st['student_id']
                status=form_data.get(f"status_{sc_id}","Absent")
                bulk_data.append((sc_id,sched_id,att_date,status,sid))

            if bulk_data:
                TeacherModel.save_bulk_attendance(bulk_data)
                TeacherModel.save_course_attendance_log(teacher_id,course_id,sched_id,att_date,semester,bulk_data)
                
        except (BusinessRuleError,ValidationError):
            raise
        except Exception as e:
            logging.exception(f"Error during sbmt attndnce service: {str(e)}")
            raise


    @staticmethod
    def get_fyp_groups_data(teacher_id:int):
        try:
            return TeacherModel.get_fyp_groups(teacher_id)
        except Exception as e:
            logging.exception(f"Error during get fyp grps service: {str(e)}")
            raise


    @staticmethod
    def manage_fyp_status(teacher_id:int,fyp_id:int,status:str):
        try:
            valid_statuses=['Approved','Rejected','In Progress','Completed']
            if status not in valid_statuses:
                raise ValidationError("Invalid status provided")
            
            
            TeacherModel.update_fyp_status(fyp_id,status)
        except ValidationError:
            raise
        except Exception as e:
            logging.exception(f"Error during mang fyp status service: {str(e)}")
            raise


    @staticmethod
    def send_fyp_message(teacher_id:int,fyp_id:int,message:str):
        try:
            msg_clean=bleach.clean(message.strip(),tags=[])
            if not msg_clean:
                raise ValidationError("Message cannot be empty")
                
            TeacherModel.add_fyp_message(fyp_id,teacher_id,msg_clean)
        except ValidationError:
            raise
        except Exception as e:
            logging.exception(f"Error during send fyp message service: {str(e)}")
            raise


    @staticmethod
    def get_submissions(teacher_id:int,section_id:int,sub_type:str):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id,teacher_id):
                raise BusinessRuleError("Unauthorized access to submissions")
                
            if sub_type not in ['assignment','quiz']:
                raise ValidationError("Invalid submission type")
                
            subs, meta=TeacherModel.get_submissions_by_type(section_id,sub_type)
            return subs,meta
        except (BusinessRuleError,ValidationError):
            raise
        except Exception as e:
            logging.exception(f"Error during get submissions service: {str(e)}")
            raise


    @staticmethod
    def grade_submission(teacher_id:int,section_id:int,sub_id:int,marks:int,total:int):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id,teacher_id):
                raise BusinessRuleError("Unauthorized grading attempt")
                
            if marks < 0 or total <= 0 or marks > total:
                raise ValidationError("Invalid marks or total marks")
                
            TeacherModel.update_submission_marks(sub_id,marks,total)
        except (BusinessRuleError,ValidationError):
            raise
        except Exception as e:
            logging.exception(f"Error during grade submission service: {str(e)}")
            raise


    @staticmethod
    def set_submission_status(teacher_id:int,section_id:int,sub_id:int,status:str):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id,teacher_id):
                raise BusinessRuleError("Unauthorized status attempt")
            valid = ['Best','Average','Worst']
            if status not in valid: raise ValidationError("Invalid status")
            
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute("UPDATE student_submissions SET submission_status=%s WHERE submission_id=%s",(status,sub_id))
                conn.commit()
            conn.close()
        except (BusinessRuleError,ValidationError):
            conn.rollback()
            raise
        except Exception as e:
            logging.exception(f"Error during set submission status: {str(e)}")
            raise




    @staticmethod
    def get_generate_result_data(teacher_id:int,section_id:int):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id,teacher_id):
                raise BusinessRuleError("Unauthorized access to grading data")

            meta=TeacherModel.get_attendance_meta(section_id)
            if not meta:
                raise NotFoundError("Class not found")

            students=TeacherModel.get_grading_data(meta['course_id'],section_id)
            return students,meta  
        except (BusinessRuleError,NotFoundError):
            raise
        except Exception as e:
            logging.exception(f"Error during get grading students service: {str(e)}")
            raise


    @staticmethod
    def submit_bulk_results(teacher_id:int,section_id:int,form_data:dict):
        try:
            if not TeacherModel.is_section_owned_by_teacher(section_id, teacher_id):
                raise BusinessRuleError("Unauthorized attempt to save grade")

            meta=TeacherModel.get_attendance_meta(section_id)
            course_id=meta['course_id']
            semester=meta['semester']
            students=TeacherModel.get_grading_data(course_id,section_id)
            for st in students:
                sid=st['student_id']
                if f"sessional_{sid}" in form_data:
                    sessional=float(form_data.get(f"sessional_{sid}",0))
                    mids=float(form_data.get(f"mids_{sid}",0))
                    final=float(form_data.get(f"final_{sid}",0))
                    total_marks=sessional+mids+final
                    if total_marks>100 or total_marks<0:
                        continue

                    percentage=(total_marks/100)*100
                    if percentage >= 85:
                        grade='A',
                        gpa=4.0
                    elif percentage >= 80:
                        grade='A-'
                        gpa=3.7
                    elif percentage >= 70:
                        grade='B'
                        gpa=3.0
                    elif percentage >= 75:
                        grade='B+'
                        gpa=3.3
                    elif percentage >= 65:
                        grade='B-'
                        gpa=2.7
                    elif percentage >= 60:
                        grade='C+'
                        gpa=2.3
                    elif percentage >= 55:
                        grade='C'
                        gpa=2.0
                    elif percentage >= 50:
                        grade='C-'
                        gpa=1.7
                    else:
                        grade='F'
                        gpa=0.0

            if total_marks > 100 or total_marks < 0:
                raise ValidationError("Total marks must be between 0 and 100")

            percentage=(total_marks / 100) * 100
            status='Pass' if grade != 'F' else 'Fail'
            data={
                'total':total_marks,
                'grade':grade,
                'gpa':gpa,
                'status':status,
                'sessional':sessional,
                'mids':mids,
                'final':final
            }
            
            TeacherModel.process_student_result(sid,section_id,course_id,semester,data)
        except (BusinessRuleError,ValidationError):
            raise
        except Exception as e:
            logging.exception(f"Error during sbmt stdnt grde service: {str(e)}")
            raise


    @staticmethod
    def submit_complaint(user_id:int,title:str,description:str):
        try:
            title_clean=bleach.clean(title.strip(),tags=[])
            desc_clean=bleach.clean(description.strip(),tags=[])
            
            if not title_clean or not desc_clean:
                raise ValidationError("Title and description cannot be empty")
                
            if len(title_clean) > 200:
                raise ValidationError("Title is too long")
                
            TeacherModel.insert_complaint_suggestion(title_clean,desc_clean,user_id)
        except ValidationError:
            raise
        except Exception as e:
            logging.exception(f"Error during sbmt complnt service: {str(e)}")
            raise   