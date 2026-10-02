import os
import bleach
from werkzeug.utils import secure_filename
from datetime import datetime as _dt
import logging
from utils.exceptions import *
from students_module.students_models import *
from werkzeug.security import check_password_hash


max_file_size=5*1024*1024

class FileService:
    @staticmethod
    def validate_upload_file(file,allowed:set)->bool:
        if not file or not file.filename:
            return False

        file.file.seek(0,2)
        file_size=file.file.tell()
        file.file.seek(0)
        if file_size==0:
            logging.warning("Upload file is empty")
            raise ValidationError("File is empty")
        
        if file_size>max_file_size:
            logging.warning(f"Upload file size exceed: {file_size}")
            raise ValidationError("File size exceed. Max limit 5MB")

        if allowed:
            ext=file.filename.rsplit('.',1)[-1].lower() if '.' in file.filename else ''
            if ext not in allowed:
                logging.warning(f"Invalid file extension: {ext}")
                raise ValidationError("Only"+", ".join(sorted(allowed)).upper()+" files are allowed")
            if ext=='pdf':
                head=file.file.read(5)
                file.file.seek(0)
                if not head.startswith(b'%PDF'):
                    logging.warning("Invalid PDF file handler")
                    raise ValidationError("The uploaded pdf is not valid")

        return True



class StudentService:
    @staticmethod
    def authenticate_student(email:str,password:str):
        try:
            user=UserModel.get_user_by_email(email)
            if not user or user['role_id'] !=2 or not check_password_hash(user['password'],password):
                logging.warning(f"Invalid Password: {str(password)}")
                raise BusinessRuleError("Invalid credentials")

            student_obj=StudentModel.get_student_by_user_id(user['user_id'])
            if not student_obj:
                logging.error(f"Student authenticate but record not found: {user['user_id']}")
                raise NotFoundError("Record not found")

            return user,student_obj
        except (BusinessRuleError,NotFoundError):
            raise
        except Exception as e:
            logging.exception(f"Unexpected error during student authenticated service: {str(e)}")


    @staticmethod
    def get_dashboard_data(student_id:int,user_id:int):
        try:
            freeze_student=CheckFreezeStatus.confirm_freeze_status(student_id)
            if freeze_student and freeze_student.get('status') == 'Approved':
                return {
                    "access_denied":True,
                    "message":"Your semester has be freeze.Kindly contact to office"
                }

            courses=StudentModel.get_enrolled_courses_by_student_id(student_id)
            if not courses:
                return {
                    "access_denied":True,
                    "message":"No enrolled courses"
                }

            course_ids=[c['course_id'] for c in courses]
            schedule=StudentModel.get_course_schedule_for_enrolled_sections(course_ids,student_id)
            course_data=StudentModel.get_course_details_by_ids(course_ids)
            course_names={c['course_id']:c['course_name'] for c in course_data}
            teacher_rows=StudentModel.get_teachers_by_course_ids(course_ids)
            all_teachers_ids=list(set(r['teacher_id'] for r in teacher_rows))
            teacher_info_list=StudentModel.get_teacher_info_by_ids(all_teachers_ids)
            teacher_name={t['teacher_id']:f"{t['first_name']} {t['last_name']}" for t in teacher_info_list}

            course_teacher_map={}
            for row in teacher_rows:
                c_id=row['course_id']
                t_name=teacher_name.get(row['teacher_id'])
                if t_name:
                    course_teacher_map.setdefault(c_id,set()).add(t_name)

            formatted_schedule=[]
            for s in schedule:
                c_id=s['course_id']
                teachers_str=", ".join(course_teacher_map.get(c_id,["N/A"]))
                schedule_id=s.get('course_schedule_id') or s.get('id') or s.get('schedule_id')
                formatted_schedule.append({
                    "course_schedule_id":schedule_id,
                    "course_name":course_names.get(c_id,'Unknown Course'),
                    "teacher_name":teachers_str,
                    "day_of_week":s['day_of_week'],
                    "start_time":s['start_time'],
                    "end_time":s['end_time'],
                    "location":s['location'],
                    "section_name":s.get('section_name','')
                })

            submissions=StudentModel.get_student_submission_status(student_id)
            return {
                "access_denied":False,
                "schedule":formatted_schedule,
                "teacher":teacher_info_list,
                "uploaded_assignments":[sub['course_id'] for sub in submissions if sub['submission_type'] == 'assignment'],
                "uploaded_quizzes":[sub['course_id'] for sub in submissions if sub['submission_type'] == 'quiz'],
                "active_notifications":NotificationModel.get_active_notifications(user_id, 'student'),
                "show_marquee":False,
                "flash_message":None
            }
        except Exception as e:
            logging.error(f"Error during get dashboard data service: {str(e)}")
            raise    


    @staticmethod
    def get_attendance_data(student_id:int):
        try:
            enrolled_courses=StudentModel.get_student_courses_for_attendance(student_id)
            if not enrolled_courses:
                return []
            
            report=[]
            for course in enrolled_courses:
                sc_id=course['student_course_id']
                total_lectures,attended=StudentModel.get_attendance_summary(sc_id)
                history=StudentModel.get_attendance_status_details(sc_id)
                perc=(attended/total_lectures * 100) if total_lectures > 0 else 0
                teacher=StudentModel.get_teacher_name_attendance(sc_id)
                teacher_name=teacher['teacher_name'] if teacher else '-'
                
                report.append({
                    "course_name":course['course_name'],
                    "credit_hours":course['credit_hours'],
                    "total_lectures":total_lectures,
                    "attended_lectures":attended,
                    "percentage":round(perc, 1),
                    "lecture_status": history,
                    "teacher_name":teacher_name
                })
            return report
        except Exception as e:
            logging.exception(f"Error during get attendance service: {str(e)}")
            raise


    @staticmethod
    def upload_fee_voucher(student_id:int,month:str,fee_amount:float,front_file,back_file):
        try:
            FileService.validate_upload_file(front_file,allowed={'jpg','jpeg','png'})
            FileService.validate_upload_file(back_file,allowed={'jpg','jpeg','png'})
            upload_folder=os.path.join(os.getcwd(),'static','uploads','students_uploads','voucher_pics')
            os.makedirs(upload_folder,exist_ok=True)
            
            front_filename=secure_filename(f"student_{student_id}_front_{front_file.filename}")
            back_filename=secure_filename(f"student_{student_id}_back_{back_file.filename}")
            
            with open(os.path.join(upload_folder,front_filename),'wb') as f:
                f.write(front_file.file.read())

            with open(os.path.join(upload_folder, back_filename),'wb') as f:
                f.write(back_file.file.read())

            program=StudentModel.get_student_by_id(student_id)
            db_front=f"uploads/students_uploads/voucher_pics/{front_filename}"
            db_back=f"uploads/students_uploads/voucher_pics/{back_filename}"
            StudentModel.upload_fee_voucher(student_id,program['program_id'],month,fee_amount,db_front,db_back)
        except ValidationError as v:
            logging.warning(f"Error validation during fee voucher service: {str(v)}")
            raise
        except Exception as e:
            logging.exception(f"Unexpected error during upload fee voucher service: {str(e)}")
            raise




    @staticmethod
    def handle_improvement_request(student_id:int,user_id:int,target_cid:int):
        try:
            if StudentModel.get_existing_improvement_request(student_id):
                logging.warning(f"Student {student_id} apply multiple course request service")
                raise BusinessRuleError("Only one subject allowed")
            
            StudentModel.add_improvement_subject(student_id,target_cid)
            StudentModel.add_notification(user_id,'student',None,'admin',
                                        'Improvement Subject Selected',
                                        f'Student {student_id} select course {target_cid} for improvement',target_cid,'Pending')
        except BusinessRuleError:
            raise    
        except Exception as e:
            logging.exception(f"Unexpected error during handle improvement service: {str(e)}")
            raise



    @staticmethod
    def handle_fail_subject_request(student_id:int,user_id:int,target_cid:int):
        try:
            if StudentModel.get_existing_retake_request(student_id):
                logging.warning(f"Student {student_id} try to handle fail subject service")
                raise BusinessRuleError("Only one subject selected for retake")
            
            StudentModel.add_fail_subject(student_id,target_cid)
            StudentModel.add_notification(user_id,'student','01','coordinator','Retake subject selected', 
                                        f'Student {student_id} select course {target_cid} for retake',target_cid,'pending')
        except BusinessRuleError:
            raise
        except Exception as e:
            logging.exception(f"Unexpected error during handle fail subject service: {str(e)}")
            raise    



    @staticmethod
    def handle_semester_freeze(student_id:int,reason: str):
        try:
            existing=StudentModel.get_active_semester_freeze_request(student_id)
            if existing and existing.get('status') in ['Pending','Approved']:
                logging.warning(f"Student {student_id} try to applied smestr freeze")
                raise BusinessRuleError("Already applied for freeze.")
            
            semester=StudentModel.get_last_recorded_semester(student_id)
            if not semester:
                raise NotFoundError("No semester record found.")
            
            StudentModel.add_semester_freeze_request(student_id,semester,reason)
        except BusinessRuleError:
            raise

        except Exception as e:
            logging.exception(f"Error during handle smstr free: {str(e)}")   
            raise 



    @staticmethod
    def handle_summer_registration(student_id:int,subject_id:int):
        try:
            summer=StudentModel.get_latest_summer_semester()
            if not summer:
                logging.warning(f"Summeer registeration handle by student: {student_id}")
                raise NotFoundError("No summer semester available")
            
            StudentModel.add_summer_subject(student_id,subject_id,summer['summer_semesters_id'])
        except NotFoundError:
            raise
        except Exception as e:
            logging.exception(f"Error during handle summer registeration: {str(e)}") 
            raise   


    @staticmethod
    def check_fyp_semester(student_id:int):
        try:
            curnt_smstr=StudentModel.get_current_semester(student_id)
            if curnt_smstr <=6:
                logging.warning(f"Student {student_id} try to open fyp page")
                raise BusinessRuleError("FYP is not available for current semester")
        except BusinessRuleError:
            raise
        except Exception as e:
            logging.exception(f"Error during check fyp smstr: {str(e)}")    
        

    @staticmethod
    def _save_fyp_file(student_id:int,file) -> str:
        try:
            FileService.validate_upload_file(file,allowed={'pdf'})    
            folder=os.path.join(os.getcwd(),'static','uploads','students_uploads','students_fyp_proposal')
            os.makedirs(folder,exist_ok=True)
            orignal=secure_filename(file.filename)[-80:]
            name=secure_filename(f"SID_{student_id}_{_dt.now().strftime('%Y%m%d_%H%M%S')}_{orignal}")
            with open(os.path.join(folder,name),'wb') as f:
                f.write(file.file.read())

            return f"uploads/students_uploads/students_fyp_proposal/{name}"
        except ValidationError:
            raise
        except Exception as e:
            logging.exception(f"Error during fyp save file: {str(e)}")
            raise



    @staticmethod
    def submit_fyp_proposal(student_id:int,project_title:str,description:str,teacher_id:int,proposal_file):
        try:
            already_fyp=StudentModel.get_fyp_project(student_id)
            if already_fyp:
                logging.warning(f"Student {student_id} try to submit fyp again")
                raise BusinessRuleError("You already submitted")

            title,desc=(project_title or "").strip(),(description or "").strip()
            if not title or len(title)>200:
                logging.warning(f"Student {student_id} try to submit without title")
                raise ValidationError("Title is required")

            if not desc:
                logging.warning(f"Student {student_id} try to submit without description")
                raise ValidationError("Description is required")

            if teacher_id and teacher_id not in {t['teacher_id'] for t in StudentModel.get_all_teachers()}:
                logging.warning(f"Student {student_id} try to select undefined teacher")
                raise NotFoundError("Selected supervisor was not found")

            db_path=None
            if proposal_file and proposal_file.filename:
                db_path=StudentService._save_fyp_file(student_id,proposal_file)

            StudentModel.insert_fyp_proposal(student_id,title,desc,teacher_id or None,db_path)    

        except (BusinessRuleError,ValidationError,NotFoundError):
            raise
        except Exception as e:
            logging.exception(f"Error during submit fyp service: {str(e)}")
            raise 



    @staticmethod
    def update_fyp(student_id:int,project_title:str,proposal_file):
        try:
            fyp=StudentModel.get_fyp_project(student_id)
            if not fyp:
                logging.warning(f"Student {student_id} fyp not found")
                raise NotFoundError("No FYP project found")

            title=(project_title or "").strip() or fyp['project_title']      
            if len(title)>200:
                logging.warning(f"Student {student_id} try to submit lengthy title")
                raise ValidationError("Title is too long")

            db_path=None
            if proposal_file and proposal_file.filename:
                db_path=StudentService._save_fyp_file(student_id,proposal_file)

            if title==fyp['project_title'] and not db_path:
                logging.warning(f"Student {student_id} try to update without any data")
                raise BusinessRuleError("Nothing to update")
            
            StudentModel.update_fyp_data(student_id,title,db_path) 

        except (BusinessRuleError,NotFoundError,ValidationError):
            raise
        except Exception as e :
            logging.exception(f"Error during update fyp service: {str(e)}")
            raise



    @staticmethod
    def upload_assignment_quiz(student_id:int,course_id:int,section_id:int,sub_type:str,file):
        try:
            FileService.validate_upload_file(file,allowed={'doc','docx','pdf'})
            folder_name='students_assignments' if sub_type == 'assignment' else 'students_quizes'
            folder=os.path.join(os.getcwd(),'static','uploads','students_uploads',folder_name)
            os.makedirs(folder,exist_ok=True)
            filename=secure_filename(f"SID_{student_id}_{_dt.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            with open(os.path.join(folder,filename),'wb') as f:
                f.write(file.file.read())

            db_path=f"uploads/students_uploads/{folder_name}/{filename}"
            StudentModel.insert_submission(student_id,course_id,section_id,db_path,sub_type)
            return filename
        except ValidationError:
            raise
        except Exception as e:
            logging.exception(f"Error during upload submission(assignmnt,quiz) service: {str(e)}")




