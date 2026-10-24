from werkzeug.security import check_password_hash,generate_password_hash
from utils.exceptions import BusinessRuleError,NotFoundError,ValidationError
from admin.admin_models import (UserModel,AdminModel,StudentModel,TeacherModel, 
                                       NotificationModel,EnrollmentModel,SalaryModel, 
                                       TimetableModel,ExamModel,AttendanceModel)
import logging

class AdminService:
    
    @staticmethod
    def authenticate_admin(email:str,password: str):
        admin_details=UserModel.get_by_email(email)
        if not admin_details or not check_password_hash(admin_details['password'],password):
            raise BusinessRuleError("Invalid email or password.")


        admin_data=AdminModel.get_admin_by_email(email)
        if not admin_data:
            raise BusinessRuleError("Access denied.You are not an admin.")

        
    
        user=UserModel.email_exists(email)
        if not user:
            raise BusinessRuleError("Invalid email or password.")
        
        admin_details['user_id']=user['user_id']

        return admin_details,admin_data

    @staticmethod
    def get_dashboard_data():
        counts=AdminModel.get_dashboard_counts()
        return{
            'students_count':counts['students'],
            'teachers_count':counts['teachers'],
            'complaints_count':counts['complaints'],
            'notifications_count':counts['notifications'],
            'exam_count':counts['exams'],
            'pending_count':counts['pending_fees'],
            'courses_count':counts['courses'],
            'fyp_count':counts['fyp'],
            'freeze_count':counts['freeze']
        }

    @staticmethod
    def register_new_student(data:dict):
        if UserModel.email_exists(data['email']):
            raise ValidationError("Email already registered.")
            
        hashed_password=generate_password_hash(data['password'])
        user_id=UserModel.create(data['email'],hashed_password, 2)
        
        StudentModel.create(user_id,data['first_name'],data['last_name'],data['email'], 
            data['contact'],data['program_id'],data['admission_session'], 
            data['last_qualification'],data['admission_date'],data['current_semester'])

    @staticmethod
    def register_new_teacher(data:dict):
        if TeacherModel.email_exists(data['email']):
            raise ValidationError("Teacher with this email already exists.")
            
        hashed_password=generate_password_hash(data['password'])
        user_id=UserModel.create(data['email'],hashed_password, 1)
        
        teacher_id=TeacherModel.create(user_id, data['first_name'],data['last_name'],data['email'], 
            data['contact_num'],data['qualification'],data['joining_date'])
        
        course_ids=data.get('course_ids',[])
        for cid in course_ids:
            TeacherModel.assign_course(teacher_id,cid)


    @staticmethod
    def enroll_student_in_course(student_id:int,course_id:int,section_id:int):
        if not section_id:
            raise ValidationError("Please select a section.")
            
        if EnrollmentModel.exists(student_id,course_id):
            raise BusinessRuleError("Student is already enrolled in this course.")
            
        EnrollmentModel.enroll(student_id,course_id)
        EnrollmentModel.add_or_restore_section(student_id,section_id)


    @staticmethod
    def add_salary_record(data:dict):
        if SalaryModel.exists(data['teacher_id'],data['month'],data['year']):
            raise BusinessRuleError("Salary Record Already Exists")
        
        SalaryModel.create(data['teacher_id'],data['month'],data['year'], 
                           data['basic_salary'],data['bonus'],data['deductions'],data['status'])


    @staticmethod
    def mark_course_attendance(data:dict):
        total_students=int(data.get('total_present',0)) + int(data.get('total_absent',0))
        schedule=AttendanceModel.get_schedule_by_section(data['section_id'])
        
        if not schedule:
            raise BusinessRuleError("No schedule found for this section.")
            
        course_schedule_id=schedule['course_schedule_id']
        semester=schedule['semester']

        AttendanceModel.insert_course_log(data['teacher_id'],data['course_id'],course_schedule_id, 
            data['attendance_date'],semester,total_students, data['total_present'],data['total_absent'])


    @staticmethod
    def add_timetable_schedule(data:dict):
        if TimetableModel.exists(data['course_id']):
            raise BusinessRuleError("Schedule Already Exist")
        
        TimetableModel.create(data['day_of_week'],data['start_time'],data['end_time'], 
            data['location'],data['course_id'],data['section_id'])


    @staticmethod
    def send_notification(sender_id:int,form_data:dict):
        NotificationModel.send(sender_id=sender_id,sender_role='admin',
            receiver_id=form_data.get('receiver_id') or None,receiver_role=form_data.get('receiver_role'),
            title=form_data.get('title'),description=form_data.get('description'),
            related_course_id=form_data.get('related_course_id') or None)


    @staticmethod
    def add_exam(data:dict):
        if ExamModel.exists(data['program_id'],data['exam_category'],data['exam_semester'],data['exam_date']):
            raise BusinessRuleError("Exam date already exists for this program,category and semester.")
        
        ExamModel.create(data['program_id'],data['exam_category'],data['exam_date'], 
            data['exam_semester'],data['start_time'],data['end_time'], data['location'],data['exam_mode'])



    @staticmethod
    def promote_student_to_next_semester(student_id:int):
        result=StudentModel.get_result_by_id(student_id)
        if not result:
            raise BusinessRuleError("No result found for this student.")

        
        if result['result_status'] != 'Pass':
            raise BusinessRuleError("Student has not passed. Cannot promote.")
        
        StudentModel.promote(student_id)