from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, current_app
from utils.auth import login_required,admin_required
from werkzeug.security import check_password_hash ,generate_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import MySQLdb.cursors
from utils.db import mysql
from .admin_models import (UserModel, AdminModel, SystemModel, ComplaintModel, StudentModel, 
                           TeacherModel, SalaryModel, EnrollmentModel, AttendanceModel, 
                           GradeModel, FeeModel, SemesterModel, TimetableModel, FYPModel, 
                           ExamModel, NotificationModel,StudentLogModel,TeacherLogModel) 

admin=Blueprint('admin', __name__, template_folder='admin_views')


@admin.route('/admin_login',methods=['GET','POST'])
def admin_login():
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        remember='remember_me' in request.form

        cursor.execute('SELECT * FROM users WHERE email=%s',(email,))
        admin_details=cursor.fetchone()

        if admin_details and check_password_hash(admin_details['password'],password):
            cursor.execute('SELECT * FROM admins WHERE email=%s',(email,))
            admin_data=cursor.fetchone()

            
            if not admin_data:
                flash('Access denied. You are not an admin.', 'danger')
                return render_template('admin_login.html')

            session['user_id']=admin_details['user_id']
            session['role']='admin'
            session['admin_id']=admin_data['admin_id']
            session.permanent=remember
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('admin_login.html')
    return render_template('admin_login.html')  
    

@admin.route('/admin_dashboard',methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    counts=AdminModel.get_dashboard_counts()
    
    return render_template(
        'admin_dashboard.html',
        students_count=counts['students'],
        teachers_count=counts['teachers'],
        complaints_count=counts['complaints'],
        notifications_count=counts['notifications'],
        exam_count=counts['exams'],
        pending_count=counts['pending_fees'],
        courses_count=counts['courses'],
        fyp_count=counts['fyp'],
        freeze_count=counts['freeze'])


@admin.route('/admin_profile',methods=['GET', 'POST'])
@admin_required
def admin_profile():
    admin_id=session.get('admin_id')
    admin_data=AdminModel.get_by_id(admin_id)
    
    if request.method=='POST':
        return redirect(url_for('admin.admin_edit'))
    
    return render_template('admin_profile.html',admin=admin_data)


@admin.route('/admin_edit',methods=['GET', 'POST'])
@admin_required
def admin_edit():
    admin_id=session.get('admin_id')

    if request.method=='POST':
        email=request.form['email']
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        contact=request.form['contact']
        
        AdminModel.update(admin_id,email,first_name,last_name,contact)
        flash("Profile updated successfully!", "success")
        return redirect(url_for('admin.admin_profile'))

    admin_data=AdminModel.get_by_id(admin_id)
    return render_template('admin_edit.html',admin=admin_data)


@admin.route('/system_settings',methods=['GET','POST'])
@admin_required
def system_settings():
    settings=SystemModel.get_all_settings()
    return render_template('system_settings.html',settings=settings)


@admin.route('/edit_settings',methods=['GET', 'POST'])
@admin_required
def edit_settings():
    if request.method=='POST':
        setting_key=request.form.get('setting_key')
        new_value=request.form.get('setting_value')
        SystemModel.update_setting(setting_key, new_value)
        flash(f"Setting '{setting_key}' updated successfully!", "success")
    return redirect(url_for('admin.system_settings'))   


@admin.route('/complaints',methods=['GET', 'POST'])
@admin_required
def complaints():
    complaints_list=ComplaintModel.get_all()
    return render_template('complaints.html',complaints=complaints_list)


@admin.route('/solve_complaint',methods=['POST'])
@admin_required
def solve_complaint():
    complt_sugst_id=request.form.get('complt_sugst_id')
    ComplaintModel.mark_solved(complt_sugst_id)
    flash('Complaint marked as solved.', 'success')
    return redirect(url_for('admin.complaints'))  



@admin.route('/system_controls',methods=['GET','POST'])
@admin_required
def system_controls():
    semesters=SemesterModel.get_all()
    return render_template('system_controls.html',semesters=semesters)



@admin.route('/add_semester',methods=['GET','POST'])
@admin_required
def add_semester():
    if request.method=='POST':
        sem_name=request.form['name']
        sem_year=request.form['year']
        sm_start=request.form['start_date']
        sm_end=request.form['end_date']
        SemesterModel.create(sem_name,sem_year,sm_start,sm_end)
        flash('Semester added successfully.', 'success')
        return redirect(url_for('admin.system_controls'))
    return redirect(url_for('admin.system_controls'))



@admin.route('/edit_semester',methods=['GET','POST'])
@admin_required
def edit_semester():
    semester_id=request.form.get('semester_id')
    if request.method=='POST':
        sem_name=request.form['name']
        sem_year=request.form['year']
        sm_start=request.form['start_date']
        sm_end=request.form['end_date']
        SemesterModel.update(semester_id,sem_name,sem_year,sm_start,sm_end)
        flash('Semester Updated successfully.', 'success')
        return redirect(url_for('admin.system_controls'))
    return redirect(url_for('admin.system_controls'))



@admin.route('/delete_semester',methods=['GET','POST'])
@admin_required
def delete_semester():
    semester_id=request.form.get('semester_id')
    if request.method=='POST':
        SemesterModel.soft_delete(semester_id)
        flash('Semester Deleted successfully.', 'success')
        return redirect(url_for('admin.system_controls'))
    return redirect(url_for('admin.system_controls'))



@admin.route('/register_student',methods=['GET','POST'])
@admin_required
def register_student():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    students=StudentModel.get_all()
    
    cursor.execute('SELECT * FROM programs')
    programs=cursor.fetchall()
    
    sessions=StudentModel.get_admission_sessions()
    return render_template('register_student.html',students=students,programs=programs,sessions=sessions)



@admin.route('/add_student', methods=['POST'])
@admin_required
def add_student():
    if request.method=='POST':
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        email=request.form['email']
        password=request.form['password']
        contact=request.form['contact']
        program_id=request.form['program_id']
        admission_session=request.form['admission_session']
        last_qual=request.form['last_qualification']
        admission_date=request.form['admission_date']
        current_semester=request.form['current_semester']

        if UserModel.email_exists(email):
            flash('Email already registered.', 'danger')
            return redirect(url_for('admin.register_student'))

        hashed_password=generate_password_hash(password)
        user_id=UserModel.create(email, hashed_password, 2)

        StudentModel.create(user_id,first_name,last_name,email,contact,program_id, 
                           admission_session,last_qual,admission_date,current_semester)
        flash('Student registered successfully.', 'success')
        return redirect(url_for('admin.register_student'))
    
    return redirect(url_for('admin.register_student'))


@admin.route('/delete_student',methods=['GET','POST'])
@admin_required
def delete_student():
    student_id=request.form.get('student_id')
    if request.method=='POST':
        StudentModel.soft_delete(student_id)
        flash('Student Deleted successfully.', 'success')
        return redirect(url_for('admin.register_student'))
    return redirect(url_for('admin.register_student'))   



@admin.route('/update_student', methods=['POST'])
@admin_required
def update_student():
    student_id=request.form.get('student_id')
    if request.method=='POST':
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        email=request.form['email']
        contact=request.form['contact']
        program_id=request.form['program_id']
        admission_session=request.form['admission_session']
        last_qual=request.form['last_qualification']
        admission_date=request.form['admission_date']

        user_id=StudentModel.get_user_id(student_id)
        StudentModel.update(student_id,first_name,last_name,email,contact,program_id, 
                           admission_session,last_qual,admission_date)
        UserModel.update_email(user_id,email)
        flash('Student Updated successfully.', 'success')
        return redirect(url_for('admin.register_student'))
    
    return redirect(url_for('admin.register_student'))    


@admin.route('/manage_attendance',methods=['GET', 'POST'])
@admin_required
def manage_attendance():
    attendance=AttendanceModel.get_all()
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT course_id,course_name FROM courses')
    courses=cursor.fetchall()
    cursor.execute('SELECT section_id,section_name FROM sections')
    sections=cursor.fetchall()

    return render_template('manage_attendance.html',attendance=attendance,courses=courses,sections=sections,)   


@admin.route('/update_attendance',methods=['POST'])
@admin_required
def update_attendance():
    attendance_id=request.form.get('attendance_id')
    attendance_status=request.form.get('attendance_status')
    AttendanceModel.update(attendance_id, attendance_status)
    flash('Attendance updated.', 'success')
    return redirect(url_for('admin.manage_attendance'))




@admin.route('/manage_grades',methods=['GET'])
@admin_required
def manage_grades():
    program_id=request.args.get('program_id', '')
    selected_semester=request.args.get('semester', '')

    results=GradeModel.get_results(program_id, selected_semester)

    for result in results:
        result['marks']=GradeModel.get_marks(result['student_result_id'])

    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT program_id,program_name FROM programs')
    programs=cursor.fetchall()

    return render_template('manage_grades.html',
                           results=results,
                           programs=programs,
                           selected_program=int(program_id) if program_id else '',
                           selected_semester=selected_semester)



@admin.route('/update_result',methods=['POST'])
@admin_required
def update_result():
    student_result_id=request.form.get('student_result_id')
    overall_gpa=request.form.get('overall_gpa')
    result_status=request.form.get('result_status')
    GradeModel.update(student_result_id,overall_gpa,result_status)
    flash('Result updated successfully.', 'success')
    return redirect(url_for('admin.manage_grades'))    



@admin.route('/fee_management',methods=['GET'])
@admin_required
def fee_management():
    fees=FeeModel.get_all()
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT program_id,program_name FROM programs')
    programs=cursor.fetchall()
    cursor.execute('SELECT student_id,first_name,last_name FROM students WHERE is_deleted=0')
    students=cursor.fetchall()

    return render_template('fee_management.html',fees=fees,programs=programs,students=students)



@admin.route('/update_fee_status',methods=['POST'])
@admin_required
def update_fee_status():
    student_fees_id=request.form.get('student_fees_id')
    fee_status=request.form.get('fee_status')
    FeeModel.update_status(student_fees_id, fee_status)
    flash('Fee status updated.', 'success')
    return redirect(url_for('admin.fee_management'))



@admin.route('/add_fee_record',methods=['POST'])
@admin_required
def add_fee_record():
    student_id=request.form.get('student_id')
    program_id=request.form.get('program_id')
    fee_amount=request.form.get('fee_amount')
    fee_month=request.form.get('fee_month')
    fee_status=request.form.get('fee_status')
    FeeModel.create(student_id,program_id,fee_amount,fee_month,fee_status)
    flash('Fee record added.', 'success')
    return redirect(url_for('admin.fee_management'))



@admin.route('/course_registration',methods=['GET'])
@admin_required
def course_registration():
    enrollments=EnrollmentModel.get_all()
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT student_id,first_name,last_name FROM students WHERE is_deleted=%s',(0,))
    students=cursor.fetchall()
    cursor.execute('SELECT course_id,course_name FROM courses WHERE is_deleted=%s',(0,))
    courses=cursor.fetchall()
    sections=EnrollmentModel.get_all_sections()

    return render_template('course_registration.html',
                           enrollments=enrollments,
                           students=students,
                           courses=courses,sections=sections)



@admin.route('/enroll_student',methods=['POST'])
@admin_required
def enroll_student():
    student_id=request.form.get('student_id')
    course_id=request.form.get('course_id')
    section_id=request.form.get('section_id')

    if not section_id:
        flash('Please select a section.', 'danger')
        return redirect(url_for('admin.course_registration'))

    if EnrollmentModel.exists(student_id, course_id):
        flash('Student is already enrolled in this course.', 'warning')
        return redirect(url_for('admin.course_registration'))

    EnrollmentModel.enroll(student_id, course_id)
    EnrollmentModel.add_or_restore_section(student_id, section_id)
    flash('Student enrolled successfully in course and section.', 'success')
    return redirect(url_for('admin.course_registration'))



@admin.route('/remove_enrollment',methods=['POST'])
@admin_required
def remove_enrollment():
    student_course_id=request.form.get('student_course_id')
    EnrollmentModel.remove(student_course_id)
    flash('Enrollment removed.','danger')
    return redirect(url_for('admin.course_registration'))



@admin.route('/stSemester_freeze',methods=['GET'])
@admin_required
def stSemester_freeze():
    freeze_requests=SemesterModel.get_all_freeze_requests()
    return render_template('stSemester_freeze.html',freeze_requests=freeze_requests)



@admin.route('/approve_request/<int:freeze_id>',methods=['POST'])
@admin_required
def approve_request(freeze_id):
    SemesterModel.update_freeze_status(freeze_id, 'Approved')
    flash('Request approved.', 'success')
    return redirect(url_for('admin.stSemester_freeze'))



@admin.route('/reject_request/<int:freeze_id>',methods=['POST'])
@admin_required
def reject_request(freeze_id):
    SemesterModel.update_freeze_status(freeze_id, 'Rejected')
    flash('Request rejected.', 'success')
    return redirect(url_for('admin.stSemester_freeze'))
         


@admin.route('/stSummer_semester',methods=['GET'])
@admin_required
def stSummer_semester():
    summer_semesters=SemesterModel.get_all_summer()

    for sem in summer_semesters:
        sem['registrations']=SemesterModel.get_summer_registrations(sem['summer_semesters_id'])

    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT semester_id,name,year FROM semester ORDER BY year DESC')
    semesters=cursor.fetchall()

    return render_template('stSummer_semester.html',summer_semesters=summer_semesters,semesters=semesters)



@admin.route('/add_summer_semester',methods=['POST'])
@admin_required
def add_summer_semester():
    name=request.form.get('name')
    year=request.form.get('year')
    start_date=request.form.get('start_date')
    end_date=request.form.get('end_date')
    status=request.form.get('status')
    previous_semester_id=request.form.get('previous_semester_id') or None
    SemesterModel.create_summer(name,year,start_date,end_date,status,previous_semester_id)
    flash('Summer semester added successfully.', 'success')
    return redirect(url_for('admin.stSummer_semester'))


@admin.route('/delete_summer_semester',methods=['POST'])
@admin_required
def delete_summer_semester():
    summer_semesters_id=request.form.get('summer_semesters_id')
    SemesterModel.delete_summer(summer_semesters_id)
    flash('Summer semester deleted.', 'danger')
    return redirect(url_for('admin.stSummer_semester'))       


@admin.route('/view_teachers',methods=['GET', 'POST'])
@admin_required
def view_teachers():
    teachers=TeacherModel.get_all()
    for teacher in teachers:
        teacher['courses']=TeacherModel.get_courses(teacher['teacher_id'])
        
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT course_id,course_name FROM courses WHERE is_deleted=%s',(0,))
    all_courses=cursor.fetchall()
    return render_template('view_teachers.html',teachers=teachers,all_courses=all_courses)


@admin.route('/delete_teacher',methods=['GET','POST'])
@admin_required
def delete_teacher():
    teacher_id=request.form.get('teacher_id')
    teacher_email=request.form.get('email')
    TeacherModel.soft_delete(teacher_id)
    UserModel.soft_delete(teacher_email)
    return redirect(url_for('admin.view_teachers'))


@admin.route('/add_teacher',methods=['GET', 'POST'])
@admin_required
def add_teacher():
    if request.method=='POST':
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        email=request.form['email']
        password=request.form['password']
        contact_num=request.form['contact_num']
        qualification=request.form['qualification']
        joining_date=request.form['joining_date']
        course_ids=request.form.getlist('course_ids')

        if TeacherModel.email_exists(email):
            flash('Teacher with this email already exists.', 'warning')
            return redirect(url_for('admin.view_teachers'))

        hashed_password=generate_password_hash(password)
        user_id=UserModel.create(email,hashed_password,1)
        teacher_id=TeacherModel.create(user_id,first_name,last_name,email,contact_num,qualification,joining_date)

        for cid in course_ids:
            cursor=mysql.connection.cursor()
            cursor.execute('INSERT INTO teacher_course(teacher_id,course_id) VALUES(%s,%s)',
                           (teacher_id,cid))
        mysql.connection.commit()

        flash('Teacher added successfully.', 'success')
        return redirect(url_for('admin.view_teachers'))

    return redirect(url_for('admin.view_teachers'))




@admin.route('/edit_teacher',methods=['GET','POST'])
@admin_required
def edit_teacher():
    teacher_id=request.form.get('teacher_id')
    if request.method=='POST':
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        email=request.form['email']
        contact_num=request.form['contact_num']
        qualification=request.form['qualification']
        joining_date=request.form['joining_date']
        course_ids=request.form.getlist('course_ids')

        user_id=TeacherModel.get_user_id(teacher_id)
        UserModel.update_email(user_id, email)
        TeacherModel.update(user_id,first_name,last_name,email,contact_num,qualification,joining_date)
        TeacherModel.set_courses(teacher_id,course_ids)
        flash('Teacher Updated successfully.', 'success')
        return redirect(url_for('admin.view_teachers'))

    return redirect(url_for('admin.view_teachers'))



@admin.route('/salary_record',methods=['GET'])
@admin_required
def salary_record():
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT teacher_id,first_name,last_name FROM teachers WHERE is_deleted=%s",(0,))
    teachers=cursor.fetchall()
    salary_records=SalaryModel.get_all()

    return render_template('salary_record.html',teachers=teachers,salary_records=salary_records)


@admin.route('/add_record',methods=['POST'])
@admin_required
def add_record():
    teacher_id=request.form.get('teacher_id')
    month=request.form['month']
    year=request.form['year']
    basic_sal=request.form['basic_salary']
    bonus=request.form['bonus']
    deduct=request.form['deductions']
    status=request.form['status']

    if SalaryModel.exists(teacher_id,month,year):
        flash('Salary Record Already Exists','danger')
        return redirect(url_for('admin.salary_record'))

    SalaryModel.create(teacher_id,month,year,basic_sal,bonus,deduct,status)
    flash('Record Added Successfully', 'success')
    return redirect(url_for('admin.salary_record'))
   


@admin.route('/update_salary',methods=['POST'])
@admin_required
def update_salary():
    salary_id=request.form.get('salary_id')
    basic_sal=request.form['basic_salary']
    bonus=request.form['bonus']
    deduct=request.form['deductions']
    status=request.form['status']

    SalaryModel.update(salary_id,basic_sal,bonus,deduct,status)
    flash('Record Updated Successfully','success')
    return redirect(url_for('admin.salary_record'))



@admin.route('/delete_salary',methods=['POST'])
@admin_required
def delete_salary():
    salary_id=request.form.get('salary_id')
    SalaryModel.soft_delete(salary_id)
    flash('Record Deleted Successfully','success')
    return redirect(url_for('admin.salary_record'))




@admin.route('/assign_classes',methods=['GET'])
@admin_required
def assign_classes():
    assignments=TeacherModel.get_all_assignments()
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT teacher_id,first_name,last_name FROM teachers WHERE is_deleted=0')
    teachers=cursor.fetchall()
    cursor.execute('''
        SELECT c.course_id,c.course_name,p.program_name
        FROM courses c
        JOIN programs p ON c.program_id=p.program_id
        WHERE c.is_deleted=0
    ''')
    courses=cursor.fetchall()

    return render_template('assign_classes.html',
                           assignments=assignments,
                           teachers=teachers,
                           courses=courses)



@admin.route('/assign_course',methods=['GET','POST'])
@admin_required
def assign_course():
    if request.method=='POST':
        teacher_id=request.form.get('teacher_id')
        course_id=request.form.get('course_id')
        TeacherModel.assign_course(teacher_id, course_id)
        return redirect(url_for('admin.assign_classes'))

    return redirect(url_for('admin.assign_classes'))    



@admin.route('/delete_course',methods=['GET','POST'])
@admin_required
def delete_course():
    teacher_course_id=request.form.get('teacher_course_id')
    if request.method=='POST':
        TeacherModel.remove_assignment(teacher_course_id)
        flash('Course Deleted successfully.', 'success')
        return redirect(url_for('admin.assign_classes'))
    
    return redirect(url_for('admin.assign_classes'))



@admin.route('/course_attendance', methods=['GET'])
@admin_required
def course_attendance():
    attendance_records=AttendanceModel.get_all_course_logs()
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT teacher_id,first_name,last_name FROM teachers WHERE is_deleted=0')
    teachers=cursor.fetchall()
    cursor.execute('SELECT course_id,course_name FROM courses WHERE is_deleted=0')
    courses=cursor.fetchall()
    cursor.execute('''
        SELECT s.section_id,s.section_name,s.semester,c.course_name
        FROM sections s
        JOIN courses c  ON s.course_id=c.course_id
        WHERE s.is_deleted=0
    ''')
    sections=cursor.fetchall()

    return render_template('course_attendance.html',
                           attendance_records=attendance_records,
                           teachers=teachers,
                           courses=courses,sections=sections)



@admin.route('/mark_course_attendance',methods=['POST'])
@admin_required
def mark_course_attendance():
    teacher_id=request.form.get('teacher_id')
    course_id=request.form.get('course_id')
    section_id=request.form.get('section_id')
    attendance_date=request.form.get('attendance_date')
    total_present=int(request.form.get('total_present', 0))
    total_absent=int(request.form.get('total_absent', 0))
    total_students=total_present + total_absent

    schedule=AttendanceModel.get_schedule_by_section(section_id)

    if not schedule:
        flash('No schedule found for this section.', 'danger')
        return redirect(url_for('admin.course_attendance'))

    course_schedule_id=schedule['course_schedule_id']
    semester=schedule['semester']

    AttendanceModel.insert_course_log(teacher_id,course_id,course_schedule_id,attendance_date, 
                                      semester,total_students,total_present,total_absent)
    flash('Attendance record added.', 'success')
    return redirect(url_for('admin.course_attendance'))



@admin.route('/class_timetable', methods=['GET'])
@admin_required
def class_timetable():
    schedules=TimetableModel.get_all()
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT course_id,course_name FROM courses')
    courses=cursor.fetchall()
    cursor.execute('SELECT section_id,section_name FROM sections')
    sections=cursor.fetchall()

    return render_template('class_timetable.html',schedules=schedules,courses=courses,sections=sections)   



@admin.route('/add_schedule',methods=['POST'])
@admin_required
def add_schedule():
    course_id=request.form.get('course_id')
    section_id=request.form.get('section_id')
    day_of_week=request.form['day_of_week']
    start_time=request.form['start_time']
    end_time=request.form['end_time']
    location=request.form['location']

    if TimetableModel.exists(course_id):
        flash('Schedule Already Exist','danger')
        return redirect(url_for('admin.class_timetable'))
    
    TimetableModel.create(day_of_week,start_time,end_time,location,course_id,section_id)
    flash('Schedule Added to the System','success')
    return redirect(url_for('admin.class_timetable'))



@admin.route('/update_schedule',methods=['POST'])
@admin_required
def update_schedule():
    course_schedule_id=request.form.get('course_schedule_id')
    day_of_week=request.form['day_of_week']
    start_time=request.form['start_time']
    end_time=request.form['end_time']
    location=request.form['location']

    TimetableModel.update(course_schedule_id,day_of_week,start_time,end_time,location)
    flash('Schedule Updated Successfully','success')
    return redirect(url_for('admin.class_timetable'))



@admin.route('/delete_schedule',methods=['POST'])
@admin_required
def delete_schedule():
    course_schedule_id=request.form.get('course_schedule_id')
    TimetableModel.soft_delete(course_schedule_id)
    flash('Schedule Deleted Successfully','success')
    return redirect(url_for('admin.class_timetable'))    





@admin.route('/get_proposals',methods=['GET'])
@admin_required
def get_proposals():
    fyp_groups=FYPModel.get_all('In Progress')
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT teacher_id,first_name,last_name FROM teachers WHERE is_deleted=%s',(0,))
    teachers=cursor.fetchall()
        
    return render_template('get_proposals.html',fyp_groups=fyp_groups,teachers=teachers) 



@admin.route('/fyp_proposals',methods=['GET'])
@admin_required
def fyp_proposals():
    fyp_groups=FYPModel.get_all()
    return render_template('fyp_proposals.html',fyp_groups=fyp_groups)



@admin.route('/updated_fyp',methods=['POST'])
@admin_required
def updated_fyp():
    fyp_id=request.form.get('fyp_id')
    fyp_status=request.form['status']
    FYPModel.update_status(fyp_id, fyp_status)
    return redirect(url_for('admin.fyp_proposals'))



@admin.route('/assign_supervisor', methods=['POST'])
@admin_required
def assign_supervisor():
    fyp_id=request.form.get('fyp_id')
    teacher_id=request.form.get('teacher_id')
    FYPModel.assign_supervisor(fyp_id, teacher_id)
    flash('Supervisor assigned successfully.', 'success')
    return redirect(url_for('admin.fyp_proposals'))



@admin.route('/admin_notifications',methods=['GET'])
@admin_required
def admin_notifications():
    notifications=NotificationModel.get_all()
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT course_id,course_name FROM courses WHERE is_deleted=%s',(0,))
    courses=cursor.fetchall()
    cursor.execute("""
        SELECT us.user_id,us.email,rl.role_type
        FROM users us
        JOIN users_role rl ON us.role_id=rl.role_id
        WHERE us.is_deleted=%s
    """,(0,))
    users=cursor.fetchall()
    return render_template('admin_notifications.html',notifications=notifications,courses=courses,users=users)



@admin.route('/send_notification',methods=['POST'])
@admin_required
def send_notification():
    receiver_role=request.form['receiver_role']
    receiver_id=request.form.get('receiver_id') or None
    related_course_id=request.form.get('related_course_id') or None
    title=request.form['title']
    description=request.form['description']
    sender_id=session['user_id']
    sender_role='admin'

    NotificationModel.send(sender_id,sender_role,receiver_id,receiver_role,title,description,related_course_id)
    flash('Notification Send Successfully','success')
    return redirect(url_for('admin.admin_notifications'))    



@admin.route('/delete_notification',methods=['POST'])
@admin_required
def delete_notification():
    notify_id=request.form.get('notif_id')
    NotificationModel.soft_delete(notify_id)
    flash('Nofitication Deleted Successfully','success')
    return redirect(url_for('admin.admin_notifications'))    

                              

@admin.route('/exam_dates',methods=['GET'])
@admin_required
def exam_dates():
    exams=ExamModel.get_all()
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * FROM programs WHERE is_deleted=%s',(0,))
    programs=cursor.fetchall()

    return render_template('exam_dates.html',exams=exams,programs=programs)


@admin.route('/add_exams',methods=['GET','POST'])
@admin_required
def add_exams():
    if request.method=='POST':
        program_id=request.form.get('program_id')
        exam_catgry=request.form.get('exam_category')
        exam_smstr=request.form.get('exam_semester')
        exam_date=request.form.get('exam_date')
        start_time=request.form.get('start_time')
        end_time=request.form.get('end_time')
        location=request.form.get('location')
        exam_mode=request.form.get('exam_mode')

        if ExamModel.exists(program_id,exam_catgry,exam_smstr,exam_date):
            flash('Exam date already exists for this program, category and semester.', 'danger')
            return redirect(url_for('admin.exam_dates'))

        ExamModel.create(program_id,exam_catgry,exam_date,exam_smstr,start_time,end_time,location,exam_mode)
        flash('Exam added successfully.', 'success')

    return redirect(url_for('admin.exam_dates'))




@admin.route('/update_exams',methods=['GET','POST'])
@admin_required
def update_exams():
    if request.method=='POST':
        exam_id=request.form.get('exam_id')
        exam_catgry=request.form.get('exam_category')
        exam_smstr=request.form.get('exam_semester')
        exam_date=request.form.get('exam_date')
        start_time=request.form.get('start_time')
        end_time=request.form.get('end_time')
        location=request.form.get('location')
        exam_mode=request.form.get('mode')
        exam_status=request.form.get('status')

        ExamModel.update(exam_id,exam_catgry,exam_date,exam_smstr,start_time,end_time,location,exam_mode,exam_status)
        flash('Exam updated successfully.', 'success')

    return redirect(url_for('admin.exam_dates'))



@admin.route('/delete_exams',methods=['POST'])
@admin_required
def delete_exams():
    exam_id=request.form.get('exam_id')
    ExamModel.soft_delete(exam_id)
    flash('Exam Deleted Successfully','success')
    return redirect(url_for('admin.exam_dates'))    



@admin.route('/promote_students',methods=['GET'])
@login_required
def promote_students():
    students=StudentModel.get_with_results()
    return render_template('promote_students.html',students=students)


@admin.route('/promote_student/<int:student_id>',methods=['POST'])
@login_required
def promote_student(student_id):
    result=StudentModel.get_result_by_id(student_id)

    if not result:
        flash('No result found for this student.', 'warning')
        return redirect(url_for('admin.promote_students'))

    if result['result_status'] != 'Pass':
        flash('Student has not passed. Cannot promote.', 'danger')
        return redirect(url_for('admin.promote_students'))

    StudentModel.promote(student_id)
    flash('Student promoted to next semester successfully!', 'success')
    return redirect(url_for('admin.promote_students'))    



@admin.route('/student_log',methods=['GET'])
@admin_required
def student_log():
    students=StudentLogModel.get_student_log()
    all_logs=StudentLogModel.acivity_log_student()
    return render_template('student_log.html',students=students,all_logs=all_logs)   



@admin.route('/teacher_log',methods=['GET'])
@admin_required
def teacher_log():
    teachers=TeacherLogModel.get_teacher_log()
    all_logs=TeacherLogModel.activity_log_teacher()    
    return render_template('teacher_log.html',teachers=teachers,all_logs=all_logs)      
    

        

