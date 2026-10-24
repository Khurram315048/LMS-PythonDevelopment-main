from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
from admin.services.admin_services import AdminService
from admin.admin_models import *
from utils.auth import get_current_admin
from utils.exceptions import BusinessRuleError, ValidationError as AppValidation, NotFoundError
from utils.csrf import verify_csrf, get_csrf_token
from jwt import create_token, refresh_token
from jose import jwt, JWTError
from config import SECRET_KEY
from pydantic import BaseModel,Field,EmailStr,ConfigDict,field_validator
from fastapi import BackgroundTasks
from utils.send_mail import send_email


router=APIRouter(dependencies=[Depends(verify_csrf)])
base_dir=Path(__file__).parent.parent
templates=Jinja2Templates(directory=[str(base_dir / "admin" / "admin_views"), str(base_dir / "templates")])
templates.env.globals["csrf_token"]=get_csrf_token


class AdminLoginRequest(BaseModel):
    email:EmailStr
    password:str
    remember_me:bool=False



@router.get('/refresh')
def refresh_session(request:Request):
    refresh_token=request.cookies.get("refresh_token")
    
    if not refresh_token:
        request.session['flash_error']="Session expired. Please login again."
        return RedirectResponse(url='/admin_login',status_code=status.HTTP_303_SEE_OTHER)

    try:
        payload=jwt.decode(refresh_token,SECRET_KEY,algorithms=["HS256"])
        new_payload={
            'user_id':payload['user_id'],
            'role':payload['role'],
            'admin_id':payload['admin_id']
        }
        access_token=create_token(new_payload)
        new_token=refresh_token(new_payload)
        response=RedirectResponse(url='/admin_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token",value=access_token,httponly=True,max_age=1800,samesite="lax")
        response.set_cookie(key="refresh_token",value=new_token,httponly=True,max_age=7*24*60*60,samesite="lax")
        return response
        
    except JWTError as je:
        logging.exception(f"JWT Refresh get route: {str(je)}")
        response=RedirectResponse(url='/admin_login',status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response



@router.get('/admin_login',response_class=HTMLResponse)
@router.post('/admin_login',response_class=HTMLResponse)
def admin_login(request:Request,email:str=Form(None),password:str=Form(None),remember_me:bool=Form(False)):
    if request.method=="GET":
        error_msg=request.session.pop('flash_error',None)
        return templates.TemplateResponse(request=request,name="admin_login.html",context={"error":error_msg})

    try:
        inputs=AdminLoginRequest(
            email=email,
            password=password,
            remember_me=remember_me
        )
        user, admin_obj=AdminService.authenticate_admin(inputs.email,inputs.password)
        token_payload={
            'user_id':user['user_id'],
            'role':'admin',
            'admin_id':admin_obj['admin_id']
        }
        access_token=create_token(token_payload)
        new_token=refresh_token(token_payload)

        response=RedirectResponse(url='/admin_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token",value=access_token,httponly=True,max_age=1800,samesite="lax")
        response.set_cookie(key="refresh_token",value=new_token,httponly=True,max_age=7*24*60*60,samesite="lax")
        return response

    except (BusinessRuleError, AppValidation) as e:
        logging.warning(f"Login error: {str(e)}")
        return templates.TemplateResponse(request=request,name="admin_login.html",context={"error":str(e)})
    except Exception as e:
        logging.exception(f"Unexpected login error: {str(e)}")
        return templates.TemplateResponse(request=request, name="admin_login.html",context={"error":"System Error"})


@router.get('/admin_dashboard')
def admin_dashboard(request:Request,current_user:dict=Depends(get_current_admin)):
    try:
        dashboard_data=AdminService.get_dashboard_data()
        dashboard_data['flash_success']=request.session.pop('flash_success', None)
        dashboard_data['flash_error']=request.session.pop('flash_error', None)
        return templates.TemplateResponse(request=request,name="admin_dashboard.html",context=dashboard_data)
    except Exception as e:
        logging.exception(f"Error during admin dashboard: {str(e)}")
        return templates.TemplateResponse(request=request,name="admin_dashboard.html",context={"error": "Try again"})


@router.get('/admin_profile')
@router.post('/admin_profile')
def admin_profile(request:Request,current_user:dict=Depends(get_current_admin)):
    admin_id=current_user['admin_id']
    if request.method=='POST':
        return RedirectResponse(url='/admin_edit',status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        admin_data=AdminModel.get_by_id(admin_id)
        return templates.TemplateResponse(request=request,name="admin_profile.html",context={
            "admin":admin_data,
            "flash_success":request.session.pop('flash_success', None)
        })
    except Exception as e:
        logging.exception(f"Error in admin profile: {str(e)}")
        return RedirectResponse(url='/admin_dashboard',status_code=status.HTTP_303_SEE_OTHER)



@router.get('/admin_edit')
@router.post('/admin_edit')
async def admin_edit(request:Request,background_tasks:BackgroundTasks,current_user:dict=Depends(get_current_admin)):
    admin_id=current_user['admin_id']
    user_id=current_user['user_id']
    if request.method=='POST':
        form_data=await request.form()
        try:
            AdminModel.update(admin_id,form_data['email'],form_data['first_name'],form_data['last_name'],form_data['contact'])
            UserModel.update_email(current_user['user_id'],form_data['email'])
            request.session['flash_success']="Profile updated successfully!"
            admin_email=AdminModel.get_email_by_user_id(user_id)
            if admin_email:
                background_tasks.add_task(send_email,[admin_email],"Profile Updated Successfully")
            return RedirectResponse(url='/admin_profile',status_code=status.HTTP_303_SEE_OTHER)
        except Exception as e:
            logging.exception(f"Error updating profile: {str(e)}")
            request.session['flash_error']="Failed to update profile."

    admin_data=AdminModel.get_by_id(admin_id)
    return templates.TemplateResponse(request=request,name="admin_edit.html",context={"admin":admin_data})



@router.get('/system_settings')
def system_settings(request:Request,current_user:dict=Depends(get_current_admin)):
    settings=SystemModel.get_all_settings()
    return templates.TemplateResponse(request=request,name="system_settings.html", context={
        "settings": settings,
        "flash_success":request.session.pop('flash_success', None)
    })


@router.post('/edit_settings')
def edit_settings(request:Request,setting_key:str=Form(...),setting_value:str=Form(...),current_user:dict=Depends(get_current_admin)):
    try:
        SystemModel.update_setting(setting_key,setting_value)
        request.session['flash_success']=f"Setting '{setting_key}' updated successfully!"
    except Exception as e:
        logging.exception(f"Error updating settings: {str(e)}")
        request.session['flash_error']="Failed to update setting."
    return RedirectResponse(url='/system_settings',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/complaints')
def complaints(request:Request,current_user:dict=Depends(get_current_admin)):
    complaints_list = ComplaintModel.get_all()
    return templates.TemplateResponse(request=request,name="complaints.html",context={
        "complaints":complaints_list,
        "flash_success":request.session.pop('flash_success', None)
    })


@router.post('/solve_complaint')
def solve_complaint(request:Request,background_tasks:BackgroundTasks,complt_sugst_id:int=Form(...),current_user:dict=Depends(get_current_admin)):
    user_email=EmailLookup.by_complaint_id(complt_sugst_id)
    try:
        ComplaintModel.mark_solved(complt_sugst_id)
        request.session['flash_success']="Complaint marked as solved."
        if user_email:
            background_tasks.add_task(send_email,[user_email],"Complaint Solved Successfully")
    except Exception as e:
        logging.exception(f"Error solving complaint: {str(e)}")
    return RedirectResponse(url='/complaints',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/system_controls')
def system_controls(request:Request,current_user:dict=Depends(get_current_admin)):
    semesters=SemesterModel.get_all()
    return templates.TemplateResponse(request=request,name="system_controls.html",context={
        "semesters":semesters,
        "flash_success":request.session.pop('flash_success', None)
    })


@router.post('/add_semester')
def add_semester(request:Request,name:str=Form(...),year:str=Form(...),start_date:str=Form(...),end_date:str=Form(...),current_user: dict = Depends(get_current_admin)):
    try:
        SemesterModel.create(name,year,start_date,end_date)
        request.session['flash_success']="Semester added successfully."
    except Exception as e:
        logging.exception(f"Error adding semester: {str(e)}")
    return RedirectResponse(url='/system_controls',status_code=status.HTTP_303_SEE_OTHER)


@router.post('/edit_semester')
def edit_semester(request:Request,semester_id:int=Form(...),name:str=Form(...),year:str=Form(...),start_date:str=Form(...),end_date:str=Form(...),current_user:dict=Depends(get_current_admin)):
    try:
        SemesterModel.update(semester_id,name,year,start_date,end_date)
        request.session['flash_success']="Semester Updated successfully."
    except Exception as e:
        logging.exception(f"Error editing semester: {str(e)}")
    return RedirectResponse(url='/system_controls',status_code=status.HTTP_303_SEE_OTHER)



@router.post('/delete_semester')
def delete_semester(request:Request,semester_id:int=Form(...),current_user:dict=Depends(get_current_admin)):
    try:
        SemesterModel.soft_delete(semester_id)
        request.session['flash_success']="Semester Deleted successfully."
    except Exception as e:
        logging.exception(f"Error deleting semester: {str(e)}")
    return RedirectResponse(url='/system_controls',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/register_student')
def register_student(request:Request,current_user:dict=Depends(get_current_admin)):
    students=StudentModel.get_all()
    programs=ProgramModel.get_all() 
    sessions=StudentModel.get_admission_sessions()
    return templates.TemplateResponse(request=request,name="register_student.html",context={
        "students": students,"programs":programs,"sessions":sessions,
        "flash_success":request.session.pop('flash_success', None),
        "flash_error":request.session.pop('flash_error', None)
    })


@router.post('/add_student')
async def add_student(request:Request,current_user:dict=Depends(get_current_admin)):
    form_data=dict(await request.form())
    try:
        AdminService.register_new_student(form_data)
        request.session['flash_success']="Student registered successfully."
    except AppValidation as e:
        request.session['flash_error']=str(e)
    except Exception as e:
        logging.exception(f"Error adding student: {str(e)}")
        request.session['flash_error']="Failed to register student."
    return RedirectResponse(url='/register_student',status_code=status.HTTP_303_SEE_OTHER)


@router.post('/update_student')
async def update_student(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        student_id = form_data['student_id']
        user_id = StudentModel.get_user_id(student_id)
        StudentModel.update(student_id, form_data['first_name'], form_data['last_name'], form_data['email'], 
                            form_data['contact'], form_data['program_id'], form_data['admission_session'], 
                            form_data['last_qualification'], form_data['admission_date'])
        UserModel.update_email(user_id, form_data['email'])
        request.session['flash_success'] = "Student Updated successfully."
    except Exception as e:
        logging.exception(f"Error updating student: {str(e)}")
    return RedirectResponse(url='/register_student', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_student')
def delete_student(request: Request, student_id: int = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        StudentModel.soft_delete(student_id)
        request.session['flash_success'] = "Student Deleted successfully."
    except Exception as e:
        logging.exception(f"Error deleting student: {str(e)}")
    return RedirectResponse(url='/register_student', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/manage_attendance')
def manage_attendance(request: Request, current_user: dict = Depends(get_current_admin)):
    attendance = AttendanceModel.get_all()
    courses = CourseModel.get_all()
    sections = EnrollmentModel.get_all_sections()
    return templates.TemplateResponse(request=request, name="manage_attendance.html", context={
        "attendance": attendance, "courses": courses, "sections": sections,
        "flash_success": request.session.pop('flash_success', None)
    })


@router.post('/update_attendance')
def update_attendance(request: Request, attendance_id: int = Form(...), attendance_status: str = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        AttendanceModel.update(attendance_id, attendance_status)
        request.session['flash_success'] = "Attendance updated."
    except Exception as e:
        logging.exception(f"Error updating attendance: {str(e)}")
    return RedirectResponse(url='/manage_attendance', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/manage_grades')
def manage_grades(request: Request, program_id: str = None, semester: str = None, current_user: dict = Depends(get_current_admin)):
    results = GradeModel.get_results(program_id, semester)
    for result in results:
        result['marks'] = GradeModel.get_marks(result['student_result_id'])
    
    programs = ProgramModel.get_all()
    return templates.TemplateResponse(request=request, name="manage_grades.html", context={
        "results": results, "programs": programs,
        "selected_program": int(program_id) if program_id else '',
        "selected_semester": semester,
        "flash_success": request.session.pop('flash_success', None)
    })


@router.post('/update_result')
def update_result(request: Request, student_result_id: int = Form(...), overall_gpa: float = Form(...), result_status: str = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        GradeModel.update(student_result_id, overall_gpa, result_status)
        request.session['flash_success'] = "Result updated successfully."
    except Exception as e:
        logging.exception(f"Error updating result: {str(e)}")
    return RedirectResponse(url='/manage_grades', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/fee_management')
def fee_management(request: Request, current_user: dict = Depends(get_current_admin)):
    fees = FeeModel.get_all()
    programs = ProgramModel.get_all()
    students = StudentModel.get_all()
    return templates.TemplateResponse(request=request, name="fee_management.html", context={
        "fees": fees, "programs": programs, "students": students,
        "flash_success": request.session.pop('flash_success', None)
    })


@router.post('/update_fee_status')
def update_fee_status(request: Request, student_fees_id: int = Form(...), fee_status: str = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        FeeModel.update_status(student_fees_id, fee_status)
        request.session['flash_success'] = "Fee status updated."
    except Exception as e:
        logging.exception(f"Error updating fee status: {str(e)}")
    return RedirectResponse(url='/fee_management', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/add_fee_record')
def add_fee_record(request: Request, student_id: int = Form(...), program_id: int = Form(...), fee_amount: float = Form(...), fee_month: str = Form(...), fee_status: str = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        FeeModel.create(student_id, program_id, fee_amount, fee_month, fee_status)
        request.session['flash_success'] = "Fee record added."
    except Exception as e:
        logging.exception(f"Error adding fee record: {str(e)}")
    return RedirectResponse(url='/fee_management', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/course_registration')
def course_registration(request: Request, current_user: dict = Depends(get_current_admin)):
    enrollments = EnrollmentModel.get_all()
    students = StudentModel.get_all()
    courses = CourseModel.get_all()
    sections = EnrollmentModel.get_all_sections()
    return templates.TemplateResponse(request=request, name="course_registration.html", context={
        "enrollments": enrollments, "students": students, "courses": courses, "sections": sections,
        "flash_success": request.session.pop('flash_success', None),
        "flash_error": request.session.pop('flash_error', None)
    })


@router.post('/enroll_student')
def enroll_student(request: Request, student_id: int = Form(...), course_id: int = Form(...), section_id: int = Form(None), current_user: dict = Depends(get_current_admin)):
    try:
        AdminService.enroll_student_in_course(student_id, course_id, section_id)
        request.session['flash_success'] = "Student enrolled successfully in course and section."
    except AppValidation as e:
        request.session['flash_error'] = str(e)
    except BusinessRuleError as e:
        request.session['flash_error'] = str(e)
    except Exception as e:
        logging.exception(f"Error enrolling student: {str(e)}")
    return RedirectResponse(url='/course_registration', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/remove_enrollment')
def remove_enrollment(request: Request, student_course_id: int = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        EnrollmentModel.remove(student_course_id)
        request.session['flash_error'] = "Enrollment removed."
    except Exception as e:
        logging.exception(f"Error removing enrollment: {str(e)}")
    return RedirectResponse(url='/course_registration', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/stSemester_freeze')
def stSemester_freeze(request: Request, current_user: dict = Depends(get_current_admin)):
    freeze_requests = SemesterModel.get_all_freeze_requests()
    return templates.TemplateResponse(request=request, name="stSemester_freeze.html", context={
        "freeze_requests": freeze_requests,
        "flash_success": request.session.pop('flash_success', None)
    })


@router.post('/approve_request/{freeze_id}')
def approve_request(request:Request,background_tasks:BackgroundTasks,freeze_id:int,current_user:dict=Depends(get_current_admin)):
    user_email=EmailLookup.by_freeze_id(freeze_id)
    try:
        SemesterModel.update_freeze_status(freeze_id,'Approved')
        request.session['flash_success']="Request approved."
        if user_email:
            background_tasks.add_task(send_email,[user_email],"Semester Freeze Request Accepted")
    except Exception as e:
        logging.exception(f"Error approving freeze request: {str(e)}")
    return RedirectResponse(url='/stSemester_freeze',status_code=status.HTTP_303_SEE_OTHER)


@router.post('/reject_request/{freeze_id}')
def reject_request(request:Request,background_tasks:BackgroundTasks,freeze_id:int,current_user:dict=Depends(get_current_admin)):
    user_email=EmailLookup.by_freeze_id(freeze_id)
    try:
        SemesterModel.update_freeze_status(freeze_id,'Rejected')
        request.session['flash_success']="Request rejected."
        if user_email:
            background_tasks.add_task(send_email,[user_email],"Semester Freeze Request Rejected")
    except Exception as e:
        logging.exception(f"Error rejecting freeze request: {str(e)}")
    return RedirectResponse(url='/stSemester_freeze',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/stSummer_semester')
def stSummer_semester(request: Request, current_user: dict = Depends(get_current_admin)):
    summer_semesters = SemesterModel.get_all_summer()
    for sem in summer_semesters:
        sem['registrations'] = SemesterModel.get_summer_registrations(sem['summer_semesters_id'])
    semesters = SemesterModel.get_all()
    return templates.TemplateResponse(request=request, name="stSummer_semester.html", context={
        "summer_semesters": summer_semesters, "semesters": semesters,
        "flash_success": request.session.pop('flash_success', None),
        "flash_error": request.session.pop('flash_error', None)
    })


@router.post('/add_summer_semester')
def add_summer_semester(request: Request, name: str = Form(...), year: str = Form(...), start_date: str = Form(...), end_date: str = Form(...), status_value: str = Form(..., alias="status"), previous_semester_id: int = Form(None), current_user: dict = Depends(get_current_admin)):
    try:
        SemesterModel.create_summer(name, year, start_date, end_date, status_value, previous_semester_id)
        request.session['flash_success'] = "Summer semester added successfully."
    except Exception as e:
        logging.exception(f"Error adding summer semester: {str(e)}")
    return RedirectResponse(url='/stSummer_semester', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_summer_semester')
def delete_summer_semester(request: Request, summer_semesters_id: int = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        SemesterModel.delete_summer(summer_semesters_id)
        request.session['flash_error'] = "Summer semester deleted."
    except Exception as e:
        logging.exception(f"Error deleting summer semester: {str(e)}")
    return RedirectResponse(url='/stSummer_semester', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/view_teachers')
def view_teachers(request: Request, current_user: dict = Depends(get_current_admin)):
    teachers = TeacherModel.get_all()
    for teacher in teachers:
        teacher['courses'] = TeacherModel.get_courses(teacher['teacher_id'])
    all_courses = CourseModel.get_all()
    return templates.TemplateResponse(request=request, name="view_teachers.html", context={
        "teachers": teachers, "all_courses": all_courses,
        "flash_success": request.session.pop('flash_success', None),
        "flash_error": request.session.pop('flash_error', None)
    })


@router.post('/add_teacher')
async def add_teacher(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        form_data['course_ids'] = (await request.form()).getlist('course_ids')
        AdminService.register_new_teacher(form_data)
        request.session['flash_success'] = "Teacher added successfully."
    except AppValidation as e:
        request.session['flash_error'] = str(e)
    except Exception as e:
        logging.exception(f"Error adding teacher: {str(e)}")
    return RedirectResponse(url='/view_teachers', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/edit_teacher')
async def edit_teacher(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        teacher_id = form_data['teacher_id']
        course_ids = (await request.form()).getlist('course_ids')
        user_id = TeacherModel.get_user_id(teacher_id)
        
        UserModel.update_email(user_id, form_data['email'])
        TeacherModel.update(user_id, form_data['first_name'], form_data['last_name'], form_data['email'], form_data['contact_num'], form_data['qualification'], form_data['joining_date'])
        TeacherModel.set_courses(teacher_id, course_ids)
        request.session['flash_success'] = "Teacher Updated successfully."
    except Exception as e:
        logging.exception(f"Error editing teacher: {str(e)}")
    return RedirectResponse(url='/view_teachers', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_teacher')
def delete_teacher(request: Request, teacher_id: int = Form(...), email: str = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        TeacherModel.soft_delete(teacher_id)
        UserModel.soft_delete(email)
        request.session['flash_success'] = "Teacher Deleted successfully."
    except Exception as e:
        logging.exception(f"Error deleting teacher: {str(e)}")
    return RedirectResponse(url='/view_teachers', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/salary_record')
def salary_record(request: Request, current_user: dict = Depends(get_current_admin)):
    teachers = TeacherModel.get_all()
    salary_records = SalaryModel.get_all()
    return templates.TemplateResponse(request=request, name="salary_record.html", context={
        "teachers": teachers, "salary_records": salary_records,
        "flash_success": request.session.pop('flash_success', None),
        "flash_error": request.session.pop('flash_error', None)
    })


@router.post('/add_record')
async def add_record(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        AdminService.add_salary_record(form_data)
        request.session['flash_success'] = "Record Added Successfully"
    except BusinessRuleError as e:
        request.session['flash_error'] = str(e)
    except Exception as e:
        logging.exception(f"Error adding salary: {str(e)}")
    return RedirectResponse(url='/salary_record', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/update_salary')
async def update_salary(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        SalaryModel.update(form_data['salary_id'], form_data['basic_salary'], form_data['bonus'], form_data['deductions'], form_data['status'])
        request.session['flash_success'] = "Record Updated Successfully"
    except Exception as e:
        logging.exception(f"Error updating salary: {str(e)}")
    return RedirectResponse(url='/salary_record', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_salary')
def delete_salary(request: Request, salary_id: int = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        SalaryModel.soft_delete(salary_id)
        request.session['flash_success'] = "Record Deleted Successfully"
    except Exception as e:
        logging.exception(f"Error deleting salary: {str(e)}")
    return RedirectResponse(url='/salary_record', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/assign_classes')
def assign_classes(request: Request, current_user: dict = Depends(get_current_admin)):
    assignments = TeacherModel.get_all_assignments()
    teachers = TeacherModel.get_all()
    courses = CourseModel.get_all()
    return templates.TemplateResponse(request=request, name="assign_classes.html", context={
        "assignments": assignments, "teachers": teachers, "courses": courses,
        "flash_success": request.session.pop('flash_success', None)
    })


@router.post('/assign_course')
def assign_course(request: Request, teacher_id: int = Form(...), course_id: int = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        TeacherModel.assign_course(teacher_id, course_id)
        request.session['flash_success'] = "Class assigned successfully."
    except Exception as e:
        logging.exception(f"Error assigning course: {str(e)}")
    return RedirectResponse(url='/assign_classes', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_course')
def delete_course(request: Request, teacher_course_id: int = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        TeacherModel.remove_assignment(teacher_course_id)
        request.session['flash_success'] = "Course Deleted successfully."
    except Exception as e:
        logging.exception(f"Error removing assigned course: {str(e)}")
    return RedirectResponse(url='/assign_classes', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/course_attendance')
def course_attendance(request: Request, current_user: dict = Depends(get_current_admin)):
    attendance_records = AttendanceModel.get_all_course_logs()
    teachers = TeacherModel.get_all()
    courses = CourseModel.get_all()
    sections = EnrollmentModel.get_all_sections()
    return templates.TemplateResponse(request=request, name="course_attendance.html", context={
        "attendance_records": attendance_records, "teachers": teachers, 
        "courses": courses, "sections": sections,
        "flash_success": request.session.pop('flash_success', None),
        "flash_error": request.session.pop('flash_error', None)
    })


@router.post('/mark_course_attendance')
async def mark_course_attendance(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        AdminService.mark_course_attendance(form_data)
        request.session['flash_success'] = "Attendance record added."
    except BusinessRuleError as e:
        request.session['flash_error'] = str(e)
    except Exception as e:
        logging.exception(f"Error marking course attendance: {str(e)}")
    return RedirectResponse(url='/course_attendance', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/class_timetable')
def class_timetable(request: Request, current_user: dict = Depends(get_current_admin)):
    schedules = TimetableModel.get_all()
    courses = CourseModel.get_all()
    sections = EnrollmentModel.get_all_sections()
    return templates.TemplateResponse(request=request, name="class_timetable.html", context={
        "schedules": schedules, "courses": courses, "sections": sections,
        "flash_success": request.session.pop('flash_success', None),
        "flash_error": request.session.pop('flash_error', None)
    })


@router.post('/add_schedule')
async def add_schedule(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        AdminService.add_timetable_schedule(form_data)
        request.session['flash_success'] = "Schedule Added to the System"
    except BusinessRuleError as e:
        request.session['flash_error'] = str(e)
    except Exception as e:
        logging.exception(f"Error adding schedule: {str(e)}")
    return RedirectResponse(url='/class_timetable', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/update_schedule')
async def update_schedule(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        TimetableModel.update(form_data['course_schedule_id'], form_data['day_of_week'], form_data['start_time'], form_data['end_time'], form_data['location'])
        request.session['flash_success'] = "Schedule Updated Successfully"
    except Exception as e:
        logging.exception(f"Error updating schedule: {str(e)}")
    return RedirectResponse(url='/class_timetable', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_schedule')
def delete_schedule(request: Request, course_schedule_id: int = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        TimetableModel.soft_delete(course_schedule_id)
        request.session['flash_success'] = "Schedule Deleted Successfully"
    except Exception as e:
        logging.exception(f"Error deleting schedule: {str(e)}")
    return RedirectResponse(url='/class_timetable', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/get_proposals')
def get_proposals(request:Request,current_user:dict=Depends(get_current_admin)):
    fyp_groups=FYPModel.get_all('In Progress')
    teachers=TeacherModel.get_all()
    return templates.TemplateResponse(request=request,name="get_proposals.html", context={
        "fyp_groups":fyp_groups,"teachers":teachers
    })


@router.get('/fyp_proposals')
def fyp_proposals(request:Request,current_user:dict=Depends(get_current_admin)):
    fyp_groups=FYPModel.get_all()
    return templates.TemplateResponse(request=request,name="fyp_proposals.html",context={
        "fyp_groups":fyp_groups,
        "flash_success":request.session.pop('flash_success', None)
    })


@router.post('/updated_fyp')
def updated_fyp(request:Request,background_tasks:BackgroundTasks,fyp_id:int=Form(...),fyp_status:str=Form(..., alias="status"),current_user:dict=Depends(get_current_admin)):
    user_email=EmailLookup.by_fyp_id(fyp_id)
    try:
        FYPModel.update_status(fyp_id,fyp_status)
        if user_email:
            background_tasks.add_task(send_email,[user_email],"FYP status Updated")
    except Exception as e:
        logging.exception(f"Error updating fyp: {str(e)}")
    return RedirectResponse(url='/fyp_proposals', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/assign_supervisor')
def assign_supervisor(request:Request,background_tasks:BackgroundTasks,fyp_id:int=Form(...),teacher_id:int=Form(...),current_user:dict=Depends(get_current_admin)):
    user_email=EmailLookup.by_fyp_id(fyp_id)
    try:
        FYPModel.assign_supervisor(fyp_id,teacher_id)
        request.session['flash_success']="Supervisor assigned successfully."
        if user_email:
            background_tasks.add_task(send_email,[user_email],"FYP Supervisor Assign")
    except Exception as e:
        logging.exception(f"Error assigning supervisor: {str(e)}")
    return RedirectResponse(url='/fyp_proposals', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/admin_notifications')
def admin_notifications(request: Request,current_user:dict=Depends(get_current_admin)):
    notifications=NotificationModel.get_all()
    courses=CourseModel.get_all()
    users=UserModel.get_all()
    return templates.TemplateResponse(request=request,name="admin_notifications.html",context={
        "notifications":notifications,"courses":courses,"users":users,
        "flash_success":request.session.pop('flash_success',None)
    })


@router.post('/send_notification')
async def send_notification(request:Request,current_user:dict=Depends(get_current_admin)):
    form_data=dict(await request.form())
    try:
        AdminService.send_notification(current_user['user_id'],form_data)
        request.session['flash_success']="Notification Send Successfully"
    except Exception as e:
        logging.exception(f"Error sending notification: {str(e)}")
    return RedirectResponse(url='/admin_notifications',status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_notification')
def delete_notification(request:Request,notif_id:int=Form(...),current_user:dict=Depends(get_current_admin)):
    try:
        NotificationModel.soft_delete(notif_id)
        request.session['flash_success']="Notification Deleted Successfully"
    except Exception as e:
        logging.exception(f"Error deleting notification: {str(e)}")
    return RedirectResponse(url='/admin_notifications',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/exam_dates')
def exam_dates(request: Request, current_user: dict = Depends(get_current_admin)):
    exams = ExamModel.get_all()
    programs = ProgramModel.get_all()
    return templates.TemplateResponse(request=request, name="exam_dates.html", context={
        "exams": exams, "programs": programs,
        "flash_success": request.session.pop('flash_success', None),
        "flash_error": request.session.pop('flash_error', None)
    })


@router.post('/add_exams')
async def add_exams(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        AdminService.add_exam(form_data)
        request.session['flash_success'] = "Exam added successfully."
    except BusinessRuleError as e:
        request.session['flash_error'] = str(e)
    except Exception as e:
        logging.exception(f"Error adding exam: {str(e)}")
    return RedirectResponse(url='/exam_dates', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/update_exams')
async def update_exams(request: Request, current_user: dict = Depends(get_current_admin)):
    form_data = dict(await request.form())
    try:
        ExamModel.update(form_data['exam_id'], form_data['exam_category'], form_data['exam_date'], form_data['exam_semester'], form_data['start_time'], form_data['end_time'], form_data['location'], form_data['mode'], form_data['status'])
        request.session['flash_success'] = "Exam updated successfully."
    except Exception as e:
        logging.exception(f"Error updating exam: {str(e)}")
    return RedirectResponse(url='/exam_dates', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/delete_exams')
def delete_exams(request: Request, exam_id: int = Form(...), current_user: dict = Depends(get_current_admin)):
    try:
        ExamModel.soft_delete(exam_id)
        request.session['flash_success'] = "Exam Deleted Successfully"
    except Exception as e:
        logging.exception(f"Error deleting exam: {str(e)}")
    return RedirectResponse(url='/exam_dates', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/promote_students')
def promote_students(request: Request, current_user: dict = Depends(get_current_admin)):
    students = StudentModel.get_with_results()
    return templates.TemplateResponse(request=request, name="promote_students.html", context={
        "students": students,
        "flash_success": request.session.pop('flash_success', None),
        "flash_error": request.session.pop('flash_error', None)
    })


@router.post('/promote_student/{student_id}')
def promote_student(request: Request, student_id: int, current_user: dict = Depends(get_current_admin)):
    try:
        AdminService.promote_student_to_next_semester(student_id)
        request.session['flash_success'] = "Student promoted to next semester successfully!"
    except BusinessRuleError as e:
        request.session['flash_error'] = str(e)
    except Exception as e:
        logging.exception(f"Error promoting student: {str(e)}")
    return RedirectResponse(url='/promote_students', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/student_log')
def student_log(request: Request, current_user: dict = Depends(get_current_admin)):
    students = StudentLogModel.get_student_log()
    all_logs = StudentLogModel.acivity_log_student()
    return templates.TemplateResponse(request=request, name="student_log.html", context={"students": students, "all_logs": all_logs})


@router.get('/teacher_log')
def teacher_log(request: Request, current_user: dict = Depends(get_current_admin)):
    teachers = TeacherLogModel.get_teacher_log()
    all_logs = TeacherLogModel.activity_log_teacher()    
    return templates.TemplateResponse(request=request, name="teacher_log.html", context={"teachers": teachers, "all_logs": all_logs})