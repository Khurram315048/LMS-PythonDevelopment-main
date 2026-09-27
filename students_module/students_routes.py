from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from students_module.students_models import UserModel,StudentModel,NotificationModel,CheckFreezeStatus
import os
from utils.auth import *
from utils.db import mysql 
from datetime import datetime,date
from fastapi import APIRouter,Depends,Request,UploadFile,File,Form,status
from students_module.schema import *
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from pathlib import Path
import MySQLdb
import MySQLdb.cursors

router=APIRouter()
base_dir=Path(__file__).parent.parent
templates=Jinja2Templates(directory=[str(base_dir / "students_module"/"students_views"),str(base_dir/"templates")])
ALLOWED_EXTENSIONS={'pdf'}

def allowed_file(filename:str)->bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@router.get('/student_login',response_class=HTMLResponse)
@router.post('/student_login',response_class=HTMLResponse)
def student_login(request:Request,email:str=Form(None),
    password:str=Form(None),
    remember_me:bool=Form(False)):

    if request.method=='GET':
        return templates.TemplateResponse(request=request, name="student_login.html")

    try:
        check_inputs=StudentLoginRequest(
            email=email,
            password=password,
            remember_me=remember_me
        )
    except ValidationError as v:
        print("Pydantic Validation Error:",v.errors())
        return templates.TemplateResponse(request=request,name="student_login.html", 
            context={"error":"Email Format Invalid"},
            status_code=status.HTTP_422_UNPROCESSSABLE_CONTENT)
    
    try:        
        user=UserModel.get_user_by_email(check_inputs.email)
        if not user:
            return templates.TemplateResponse(
                request=request, 
                name="student_login.html", 
                context={"error": "User not found"},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if user['role_id'] != 2:
            return templates.TemplateResponse(
                request=request,name="student_login.html", 
                context={"error":"Only student can login"},
                status_code=status.HTTP_403_FORBIDDEN
            )

        if user and check_password_hash(user['password'],check_inputs.password):
            student_obj=StudentModel.get_student_by_user_id(user['user_id'])
            if student_obj:
                request.session['user_id']=user['user_id']
                request.session['role']='student'
                request.session['student_id']=student_obj['student_id']
                request.session['date']=datetime.now().isoformat()
                request.session['remember']=remember_me
                return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
            else:
                return RedirectResponse(url='/student_login',status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:  
        print(f"Error during login route: {str(e)}")      
        return templates.TemplateResponse(request=request,name="student_login.html",context={
                                    "error":"Invalid credentials"})







@router.get('/student_base')
def student_base(request:Request,current_user:dict=Depends(get_current_student)):
    user_id=current_user['user_id']

    try:
        student_name=StudentModel.get_student_name_by_user_id(user_id)
        return templates.TemplateResponse(request=request,name="student_base.html",
                                              context={"student_name":student_name})
    except Exception as e:
        print(f"Error for student base: {str(e)}")
        return RedirectResponse(url='/student_dashboard.html',status_code=303)    





@router.get('/student_profile')
def student_profile(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        student_obj=StudentModel.get_student_by_id(student_id)
        if not student_obj:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                                context={"message":"No Student Record Found"})
        program=StudentModel.get_student_program_details(student_id)
        if not program:
            return templates.TemplateResponse(request=request,name="student_profile.html",
                                                context={"message":"No program found"})
        return templates.TemplateResponse(
                request=request,name="student_profile.html",context={
                "student_obj":student_obj,"program":program})
    except Exception as e:
        return templates.TemplateResponse(
                    request=request,
                    name="student_dashboard.html",
                    context={"error": f"Dashboard Error: {str(e)}"}
                )

        


@router.get('/student_dashboard')
def student_dashboard(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    user_id=current_user['user_id']
    try:
        print(f"Current user id: {user_id}")
        print(f"current student id: {student_id}")
        freeze_status=CheckFreezeStatus.confirm_freeze_status(student_id,)
        print(f"freeze status: {freeze_status}")
        if freeze_status and freeze_status.get('status') == 'Approved':
            return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                              context={"message":"Your Semester has been freezed.To view Dashboard kindly visit the office",
                                                       "courses":[],"schedule":[],"show_marque":True})

        courses=StudentModel.get_enrolled_courses_by_student_id(student_id,)
        print(f"courses are: {courses}")
        if not courses:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",context={"message":"No enrolled courses","courses":[],"schedule":[]})

        course_ids=[course['course_id'] for course in courses]
        schedule=StudentModel.get_course_schedule_for_enrolled_sections(course_ids,student_id)
        print(f"Shedule: {schedule}")
        course_data=StudentModel.get_course_details_by_ids(course_ids)
        course_names={c['course_id']: c['course_name'] for c in course_data}
        teacher_rows=StudentModel.get_teachers_by_course_ids(course_ids)
        all_teacher_ids=list(set(r['teacher_id'] for r in teacher_rows))
        teacher_info_list=StudentModel.get_teacher_info_by_ids(all_teacher_ids)
        teacher_names={t['teacher_id']: f"{t['first_name']} {t['last_name']}" for t in teacher_info_list}
        course_teacher_map={}
        for row in teacher_rows:
            c_id=row['course_id']
            t_name=teacher_names.get(row['teacher_id'])
            if t_name:
                if c_id not in course_teacher_map:
                    course_teacher_map[c_id]=set()
                    course_teacher_map[c_id].add(t_name)

        formatted_schedule=[]
        for s in schedule:
            c_id=s['course_id']
            teachers_str=", ".join(course_teacher_map.get(c_id, ["N/A"]))
            schedule_id=s.get('course_schedule_id') or s.get('id') or s.get('schedule_id')
            formatted_schedule.append({
                "course_schedule_id":schedule_id,
                "course_name":course_names.get(c_id, 'Unknown Course'),
                "teacher_name":teachers_str,
                "day_of_week":s['day_of_week'],
                "start_time":s['start_time'],
                "end_time":s['end_time'],
                "location":s['location'],
                "section_name":s.get('section_name', '')
                })
        submissions=StudentModel.get_student_submission_status(student_id)
        uploaded_assignments=[sub['course_id'] for sub in submissions if sub['submission_type'] == 'assignment']
        uploaded_quizzes=[sub['course_id'] for sub in submissions if sub['submission_type'] == 'quiz']
        active_notifications=NotificationModel.get_active_notifications(user_id,'student')
        exam_data=None
        admit_card=None
        show_marquee=False
        flash_message=None
        student_row=StudentModel.get_program_id_student(student_id)

        if student_row:
            program_id=student_row['program_id']
            exam_details=StudentModel.get_exam_details_student(program_id)
            print(f"Exam details: {exam_details}")
            
        today=date.today()
        upcoming=[ex for ex in exam_details if ex['exam_date'] >= today]

        if upcoming:
            exam_data=upcoming
            show_marquee=True
            student_info=StudentModel.get_student_details(student_id)

            exam_category=upcoming[0]['exam_category']
            exam_location=upcoming[0]['location'] or 'Class Room'

            admit_courses=[{
                'course_id':c['course_id'],
                'course_name':c['course_name'],
                'exam_type':exam_category,
                'location':exam_location,
                'status':'Allowed',
                } for c in course_data]
                            
            admit_card={
                'student':student_info,
                'courses':admit_courses,
                'exam_date':upcoming[0]['exam_date'],
                'start_time':upcoming[0]['start_time'],
                'end_time':upcoming[0]['end_time'],
                }
            

        return templates.TemplateResponse(request=request,name="student_dashboard.html",
                    context={"schedule":formatted_schedule,"teacher":teacher_info_list,
                        "uploaded_assignments":uploaded_assignments,"teacher_ids":{},
                        "uploaded_quizzes": uploaded_quizzes,"active_notifications":active_notifications,
                        "exam_data":exam_data,"admit_card":admit_card,
                        "show_marquee":show_marquee,"flash_message":flash_message})
    except Exception as e:
        print(f"Error during dashboard: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                          context={"error":"Try Again"})

    
   

    
@router.get('/student_fee')
def student_fee(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        fee_records_raw=StudentModel.get_student_fee_records(student_id)
        check_records=[FeeRecordHelper(
            program=str(row['program']),
            month=str(row['month']) if row['month'] else 'N/A',
            fee_amount=float(row['fee_amount']),
            paid_date=row['paid_date'],
            status=str(row['status']),
            front_voucher=row['front_voucher'] if row['front_voucher'] else '',
            back_voucher=row['back_voucher'] if row['back_voucher'] else ''
            )
            for row in fee_records_raw
            ]
            
        return templates.TemplateResponse(request=request,name="student_fee.html",context={"fee_records":check_records})     
    except Exception as e:
        return templates.TemplateResponse(
            request=request,name="student_fee.html",  
            context={"error":f"Error loading fee records: {e}"}
        )   





@router.get('/complaint_suggestion')
@router.post('/complaint_suggestion')
def complaint_suggestion(request:Request,title:str=Form(None),description:str=Form(None),current_user:dict=Depends(get_current_student)):
    user_id=current_user['user_id']

    if request.method=='GET':
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html")

    try:
        check_data=ComplaintSuggestionRequest(title=title,description=description)
    except ValidationError:
        error_msg="Title and description must be of defined length"
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html",
                                          context={"error_msg":error_msg})

    try:
        StudentModel.insert_complaint_suggestion(check_data.title,check_data.description,user_id)     
        request.session['flash_success']="Complaint/Suggestion submitted successfull"
        return RedirectResponse(url='/notifications',status_code=303)
    except Exception as e:
        print(f"Error while inserting complaint or suggestion: {str(e)}")
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html",
        context={"error":"Failed to submitted.PLease try again!"})    





@router.get('/notifications')
def notifications(request:Request,current_user:dict=Depends(get_current_student)):
    user_id=current_user['user_id']
    try:
        complaint_status=StudentModel.get_complaint_status(user_id)
        msg=request.session.get('flash_success')
        return templates.TemplateResponse(request=request,name="notifications.html",context={'complaint_status':complaint_status,'msg':msg})
    except Exception as e:
        print(f"Error: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_dashboard.html")


@router.get('/upload_fee')
@router.post('/upload_fee')
def upload_fee(request:Request,month:str=Form(None),fee_amount:float=Form(None),front_voucher:UploadFile=File(None),back_voucher:UploadFile=File(None),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    

    if request.method=='GET':
        return templates.TemplateResponse(request=request,name="upload_fee.html")

    try:
        voucher_data=UploadFeeVoucherRequest(
            month=month,fee_amount=fee_amount
        )
    except ValidationError as e:
        return templates.TemplateResponse(request=request,name="upload_fee.html",
        context={"error":"Please enter valid details"})

    if not front_voucher or not front_voucher.filename or not back_voucher or not back_voucher.filename:
        return templates.TemplateResponse(request=request,name="upload_fee.html",
        context={"error":"Both front and back voucher uploaded"})

    upload_folder=os.path.join(os.getcwd(),'static','uploads','students_uploads','voucher_pics')
    front_filename=secure_filename(f"student_{student_id}_front_{front_voucher.filename}")
    back_filename=secure_filename(f"student_{student_id}_back_{back_voucher.filename}")
    front_full_path=os.path.join(upload_folder,front_filename)
    back_full_path=os.path.join(upload_folder,back_filename)
    with open(front_full_path,'wb') as f:
        f.write(front_voucher.file.read())
    with open(back_full_path,'wb') as f:
        f.write(back_voucher.file.read())     

    db_front_path=f"uploads/students_uploads/voucher_pics/{front_filename}"
    db_back_path=f"uploads/students_uploads/voucher_pics/{back_filename}"
    try:
        program_details=StudentModel.get_student_by_id(student_id)
        program_id=program_details['program_id']
        StudentModel.upload_fee_voucher(student_id,program_id,voucher_data.month,voucher_data.fee_amount,db_front_path,db_back_path)
        request.session['flash_success']="Fee voucher uploaded successfully"
        return RedirectResponse(url='/student_fee',status_code=303)       
    except Exception as e:
        print(f"Database inser error: {str({e})}")
        return templates.TemplateResponse(request=request,name="upload_fee.html",
        context={"error":f"Failed to upload: {str({e})}"})




@router.get('/view_attendence')
def view_attendence(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        enrolled_courses=StudentModel.get_student_courses_for_attendance(student_id)
        if not enrolled_courses:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                                        context={"message":"No enrolled course found"})
        attendance_report=[]
        for course in enrolled_courses:
            sc_id=course['student_course_id']
            total_lectures,attended=StudentModel.get_attendance_summary(sc_id)
            history=StudentModel.get_attendance_status_details(sc_id)
            perc=(attended/total_lectures*100) if total_lectures>0 else 0
            
            teacher=StudentModel.get_teacher_name_attendance(sc_id)
            teacher_name=teacher['teacher_name'] if teacher else '-'
            check_records=[AttendanceRecordHelper(
                attendance_date=record['attendance_date'],
                attendance_status=record['attendance_status']
            ) for record in history]

            course_record=CourseAttendanceHelper(
                course_name=course['course_name'],
                credit_hours=course['credit_hours'],
                total_lectures=total_lectures,
                attended_lectures=attended,
                percentage=round(perc,1),
                lecture_status=check_records,
                teacher_name=teacher_name
                )
            attendance_report.append(course_record)
                
                
            return templates.TemplateResponse(request=request,name="view_attendence.html",context={"attendance_report":attendance_report})
    except Exception as e:
        print(f"Error during attendance: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_login.html",
        context={"error":f"Error : {e}"})        
    
   
    




@router.get('/view_grades')
def view_grades(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']

    try:
        student_details=StudentModel.get_student_by_id(student_id)
        if not student_details:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",context={"message":"Student details not found"}) 
        all_marks=StudentModel.get_student_results_with_marks(student_id)
        if not all_marks:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                                  context={"message":"No grades found"})

        check_marks=[GradeHelper(
            semester=row['semester'],
            course_name=row['course_name'],
            credit_hours=row['credit_hours'],
            total_marks=row['total_marks'],
            subject_gpa=row['subject_gpa'],
            status=row['status']
            ) for row in all_marks]
        return templates.TemplateResponse(request=request,name="view_grades.html",context={"student_details":student_details,"all_marks":check_marks})
    except Exception as e:
        print(f"Error duing view grades routes: {str(e)}")
        return templates.TemplateResponse(
            request=request,name="student_login.html",
            context={"error":"Login Again"}
        )     


@router.get('/course_registeration')
def course_registeration(request: Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']

    flash_success=request.session.pop('flash_success',None)
    flash_error=request.session.pop('flash_error',None)
    try:
        student=StudentModel.get_student_by_id(student_id)
        is_reg_open=StudentModel.get_system_setting('is_course_reg_open')
        if str(is_reg_open) != '1':
            return templates.TemplateResponse(request=request,name="course_registeration.html",
                                                context={"student":student,"reg_closed":True,"selected":[],
                        "can_register":False,"failed_count":0})

        improvements=list(StudentModel.get_improvement_subjects(student_id) or [])
        retakes=list(StudentModel.get_retake_subjects(student_id) or [])
        selected=improvements + retakes
        return templates.TemplateResponse(request=request,name="course_registeration.html",context={
                    "student":student,"selected":selected,"reg_closed":False,
                    "can_register":True,"flash_success":flash_success,"flash_error":flash_error})
    except Exception as e:
        print(f"Error during course registration: {str(e)}")
        return templates.TemplateResponse(request=request,name="course_registeration.html",
            context={"error":"Try Again"}
        )   




@router.get('/improvement_subject')
def improvement_subject(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        existing=StudentModel.get_existing_improvement_request(student_id)
        if existing:
            request.session['flash_error']="Only one subject for improvement"
            return RedirectResponse(url='/course_registeration',status_code=303)

        max_semester=StudentModel.get_max_semester_passed(student_id)
        if max_semester <1:
            request.session['flash_error']="NO previous semester found"
            return RedirectResponse(url='/course_registeration',status_code=303)

        courses=StudentModel.get_eligible_improvement_courses(student_id,max_semester)
        return templates.TemplateResponse(request=request,name="improvement_subject.html",
        context={"courses":courses})
    except Exception as e:
        print(f"Error during improvement subject: {str(e)}")
        return templates.TemplateResponse(request=request,name="course_registeration.html",
                                          context={"error":"Try Again"})
    





@router.post('/delete_improvement/{improvement_id}')
def delete_improvement(request:Request,improvement_id:int,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    try:
        StudentModel.delete_improvement_subject(improvement_id,student_id)
        request.session['flash_success']="Improvement subject deleted successfully"
        return RedirectResponse(url='/course_registeration',status_code=303)
    except Exception as e:
        print(f"Error while deleting the improvement: {str(e)}")
        return templates.TemplateResponse(request=request,name="course_registeration.html",
        context={"error":"Try again!"})
        







@router.post('/select_improvement/{course_id}')
def select_improvement(request:Request,course_id:int,form_course_id:int=Form(None),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    user_id=current_user['user_id']
   
    target_cid=form_course_id or course_id
    try:
        already=StudentModel.get_existing_improvement_request(student_id)
        if not already:
            StudentModel.add_improvement_subject(student_id,target_cid)
            try:
                title='Improvement Subject Selected'
                description=f'Student {student_id} select course {target_cid} for improvement'
                StudentModel.add_notification(user_id,'student',None,'admin',title,description,target_cid,'Pending')
            except Exception as e:
                print(f"Notification error: {str(e)}")

        request.session['flash_success']="Improvement subject requested successfully!"

    except Exception as e:
        print(f"Error selecting imprvement: {str(e)}")
        request.session['flash_error']="Failed to select improvement subject"

    return RedirectResponse(url='/course_registeration',status_code=303)            




@router.get('/help_desk')
@router.post('/help_desk')
def help_desk(request:Request):
    return templates.TemplateResponse(request=request,name="help_desk.html")





@router.get('/fail_subjects')
def fail_subjects(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    try:
        existing=StudentModel.get_existing_retake_request(student_id)
        if existing:
            request.session['flash_error']="Only one subject selected for retake"
            return RedirectResponse(url='/course_registeration',status_code=303)

        max_semester=StudentModel.get_max_semester_passed(student_id)
        if max_semester<1:
            request.session['flash_error']="No previous semester"
            return RedirectResponse(url='/course_registeration',status_code=303)

        courses=StudentModel.get_eligible_fail_subjects(student_id,max_semester)
        return templates.TemplateResponse(request=request,name="fail_subjects.html",
                                              context={"courses":courses})
    except Exception as e:
        print(f"Error during fail subject: {str(e)}")
        return RedirectResponse(url='/course_registeration',status_code=303)    






@router.post('/select_fail/{course_id}')
def select_fail(request:Request,course_id:int,form_course_id:int=Form(None),current_user:dict=Depends(get_current_student)):
    user_id=current_user['user_id']
    student_id=current_user['student_id']

    target_cid=form_course_id or course_id
    try:
        already=StudentModel.get_existing_retake_request(student_id)
        if not already:
            StudentModel.add_fail_subject(student_id,target_cid)
            title='Retake subject selected'
            description=f'Student {student_id} select course {target_cid} for retake'
            StudentModel.add_notification(user_id,'student','01','coordinator',title,description,target_cid,'pending')
            request.session['flash_success']="Retake subject request successfully!"
    except Exception as e:
        print(f"Error during retake: {str(e)}")
    return RedirectResponse(url='/course_registeration',status_code=303)                



@router.post('/delete_fail/{fail_id}')
def delete_fail(request:Request,fail_id:int,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        StudentModel.delete_fail_subject(fail_id,student_id)
        request.session['flash_success']="Retake subject removed successfully"
    except Exception as e:
        print(f"Error during delete fail subject: {str(e)}")
        request.session['flash_error']="Failed to remove retake subject"

    return RedirectResponse(url='/course_registeration',status_code=303)    




@router.get('/semester_freeze')
@router.post('/semester_freeze')
def semester_freeze(request:Request,reason:str=Form(None),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    try:
        student=StudentModel.get_student_by_id(student_id)
        existing_request=StudentModel.get_active_semester_freeze_request(student_id)
        semester=StudentModel.get_last_recorded_semester(student_id)
        if existing_request:
            return templates.TemplateResponse(request=request,name="semester_freeze.html",context={"existing_request":existing_request,"already_applied":True,
                "semester":semester})

        if request.method=='POST':
            try:
                freeze_input=SemesterFreezeRequest(reason=reason)
            except ValidationError:
                return templates.TemplateResponse(request=request,name="semester_freeze.html",context={
                            "semester":semester,"student":student,"already_applied":False,
                            "error":"Reason must be between 10 and 1000 characters."})

            if not semester:
                return templates.TemplateResponse(request=request,name="semester_freeze.html",context={
                            "error":"No semester record found."})
                
            StudentModel.add_semester_freeze_request(student_id,semester,freeze_input.reason)
            request.session['flash_success']="Your semester freeze request has been submitted successfully!"
            return RedirectResponse(url='/semester_freeze',status_code=303)

        return templates.TemplateResponse(request=request,name="semester_freeze.html", 
                                        context={"semester":semester,"student":student,"already_applied":False})
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Semester freeze error: {e}")
        return RedirectResponse(url='/student_dashboard',status_code=303)

    



@router.get('/summer_semester')
def summer_semester(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    try:
        student=StudentModel.get_student_by_id(student_id)
        is_summer_open=StudentModel.get_system_setting('is_summer_app_open')
        if str(is_summer_open) != '1':
            return templates.TemplateResponse(request=request,name="summer_semester.html",
            context={"student":student,"summer_closed":True,"latest_summer":None,
                         "selected":[],"can_register":False,"failed_count":0})
        
        latest_summer=StudentModel.get_latest_summer_semester()
        selected_subjects=[]
        failed_subjects=[]
        can_register=False
        if latest_summer:
            summer_id=latest_summer['summer_semesters_id']
            selected_subjects=StudentModel.get_selected_summer_subjects(student_id,summer_id)
            failed_subjects=StudentModel.get_eligible_summer_failed_subjects(student_id)
            if (failed_subjects and len(selected_subjects)<len(failed_subjects) and latest_summer.get('status') == 'Open'):
                can_register=True

            return templates.TemplateResponse(request=request,name="summer_semester.html",context={"student":student,"selected":selected_subjects,
                    "can_register":can_register,"failed_count":len(failed_subjects),
                    "latest_summer":latest_summer,"summer_closed":False})        
    except Exception as e:
        print(f"Error for summer subject: {e}")
        return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                          context={"error":"Try again"})

   
    
@router.get('/summer_subjects')
def summer_subjects(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        latest_summer=StudentModel.get_latest_summer_semester()
        if not latest_summer:
            request.session['flash_error']="No active summer semester"
            return RedirectResponse(url='/summer_semester')

        summer_semester_id=latest_summer['summer_semesters_id']
        failed_subjects=StudentModel.get_eligible_summer_failed_subjects(student_id)
        selected_subjects=StudentModel.get_selected_summer_subjects(student_id,summer_semester_id)
        selected_ids=[s['course_id'] for s in selected_subjects]
        available_subjects=[sub for sub in failed_subjects if sub['course_id'] not in selected_ids]
        return templates.TemplateResponse(request=request,name="summer_subjects.html",context={"subjects":available_subjects})
    except Exception as e:
        print(f"Error for summer subjects: {e}")
        return RedirectResponse(url='/summer_semester')



@router.post('/select_summer_subject/{subject_id}')
def select_summer_subject(request:Request,subject_id:int,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    try:
        summer_semester=StudentModel.get_latest_summer_semester()
        if not summer_semester:
            request.session['flash_error']="No summer semester available"
            return RedirectResponse(url='/summer_semester')

        summer_id=summer_semester['summer_semesters_id']
        StudentModel.add_summer_subject(student_id,subject_id,summer_id)
        request.session['flash_success']="Subject add for summer semester"
        return RedirectResponse(url='/summer_semester',status_code=303)
    except Exception as e:
        print(f"Error for summer selecting subjects: {e}")
    return templates.TemplateResponse(request=request,name="summer_semester.html",
                                              context={"error":"Try again"})        




@router.post('/delete_summer_subject/{subject_id}')
def delete_summer_subject(request:Request,subject_id:int,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']

    try:
        summer_semester=StudentModel.get_latest_summer_semester()
        if summer_semester:
            summer_id=summer_semester['summer_semesters_id']
            StudentModel.delete_summer_subject(student_id,subject_id,summer_id)
            request.session['flash_success']="Subject removed from summer semester"
            return RedirectResponse(url='/summer_semester',status_code=303)
    except Exception as e:
        print(f"Error while removing summer subject: {e}")
        return templates.TemplateResponse(request=request,name="summer_semester.html",
        context={"error":"Try again"})           
     
    return RedirectResponse(url='/summer_semester',status_code=303)




@router.get('/student_fyp')
def student_fyp(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    flash_success=request.session.pop('flash_success',None)
    flash_error=request.session.pop('flash_error',None)
    try:
        student_obj=StudentModel.get_student_by_id(student_id)
        fyp_project=StudentModel.get_fyp_project(student_id)
        teacher_details=None
        all_teachers=StudentModel.get_all_teachers()
        messages_list=[]
        if fyp_project:
            messages_list=StudentModel.get_fyp_messages(fyp_project['fyp_id'])
            if fyp_project.get('teacher_id'):
                teacher_details=StudentModel.get_teacher_full_details(fyp_project['teacher_id'])
            
        return templates.TemplateResponse(request=request,name="student_fyp.html",
            context={"student":student_obj,"fyp":fyp_project,"messages":messages_list,
                         "teacher":teacher_details,"all_teachers":all_teachers,
                         "flash_success":flash_success,"flash_error":flash_error})     
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error during fyp: {str(e)}")
        return RedirectResponse(url='/student_dashboard',status_code=303)




@router.post('/submit_fyp')
def submit_fyp(request:Request,project_title:str=Form(...),description:str=Form(...),proposal_file:UploadFile=File(None),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    

    upload_folder=os.path.join(os.getcwd(),'static','uploads','students_uploads','students_fyp_proposal')
    db_file_path=None
    if proposal_file and proposal_file.filename:
        if not allowed_file(proposal_file.filename):
            request.session['flash_error']="Only pdf type allowed"
            return RedirectResponse(url='/student_fyp',status_code=303)

        filename=secure_filename(proposal_file.filename)
        unique_name=f"SID_{student_id}_{filename}"
        file_path=os.path.join(upload_folder,unique_name)
        contents=proposal_file.file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)

        db_file_path=f"uploads/students_uploads/students_fyp_proposal/{unique_name}"
    try:    
        StudentModel.insert_fyp_proposal(student_id,project_title,description,None,db_file_path)
        request.session['flash_success']="FYP proposal submitted successfully"
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Errors submitted fyp proposal: {e}")

    return RedirectResponse(url='/student_fyp',status_code=303)        



@router.post('/send_fyp_message/{fyp_id}')
def send_fyp_message(request:Request,fyp_id:int,message:str=Form(...),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        fyp=StudentModel.get_fyp_by_id_and_student(fyp_id,student_id)
        if not fyp:
            request.session['flash_error']="Not access available"
            return RedirectResponse(url='/student_fyp',status_code=303)

        if message and message.strip():
            StudentModel.insert_fyp_message(fyp_id,student_id,'student',message.strip())
    except Exception as e:
        print(f"Error for sending fyp message: {str(e)}")
    return RedirectResponse(url='/student_fyp',status_code=303)            



@router.post('/update_fyp')
def update_fyp(request:Request,project_title:str=Form(...),proposal_file:UploadFile=File(None),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    upload_folder=os.path.join(os.getcwd(),'static','uploads','students_uploads','students_fyp_proposal')
    db_file_path=None
    if proposal_file and proposal_file.filename:
        if not allowed_file(proposal_file.filename):
            request.session['flash_error']="Only pdf files allowed"
            return RedirectResponse(url='/student_fyp',status_code=303)

        filename=secure_filename(proposal_file.filename)
        unique_name=f"SID_{student_id}_{filename}"
        file_path=os.path.join(upload_folder,unique_name)
        contents=proposal_file.file.read()
        with open(file_path,'wb') as f:
            f.write(contents)
        db_file_path=f"uploads/students_uploads/students_fyp_proposal/{unique_name}"
    try:
        StudentModel.update_fyp_data(student_id,project_title,db_file_path)
        request.session['flash_success']="Fyp project updated"
    except Exception as e:
        print(f"Error during updating fyp: {str(e)}")

    return RedirectResponse(url='/student_fyp',status_code=303)                




@router.get('/my_submissions')
def my_submissions(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    flash_success=request.session.pop('flash_success', None)
    flash_error=request.session.pop('flash_error', None)

    try:
        courses=StudentModel.get_enrolled_courses_by_student_id(student_id)
        if not courses:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",context={"message":"No course found"})
           
        course_ids=[c['course_id'] for c in courses]
        course_data=StudentModel.get_course_details_by_ids(course_ids)
        course_names={c['course_id']: c['course_name'] for c in course_data}
        schedule=StudentModel.get_course_schedule_for_enrolled_sections(course_ids,student_id)
        for s in schedule:
            s['course_name']=course_names.get(s['course_id'])

        submissions=StudentModel.get_student_submission_status(student_id)
        assignment_marks={}
        quiz_marks={}
        assignment_total={}
        quiz_totals={}
        for sub in submissions:
            cid=int(sub['course_id'])
            if sub['submission_type']=='assignment':
                assignment_marks[cid]=sub['marks']
                assignment_total[cid]=sub['total_marks']
            elif sub['submission_type']=='quiz':
                quiz_marks[cid]=sub['marks']
                quiz_totals[cid]=sub['total_marks']
        uploaded_assignments=list(assignment_marks.keys())
        uploaded_quizzes=list(quiz_marks.keys())

        return templates.TemplateResponse(request=request,name="my_submissions.html",
                    context={'schedule':schedule,'uploaded_assignments':uploaded_assignments,'assignment_marks':assignment_marks,
                        'uploaded_quizzes':uploaded_quizzes,'quiz_marks':quiz_marks,'assignment_totals':assignment_total,
                        'quiz_totals':quiz_totals,'flash_success':flash_success,
                    'flash_error':flash_error})
    except Exception as e:
        return templates.TemplateResponse(request=request,name="student_dashboard.html",
        context={"error":f"Error : {e}"})        


              


@router.post('/upload_submission')
def upload_submission(request:Request,course_id:int=Form(...),section_id:int=Form(...),type:str=Form(...),file:UploadFile=File(...),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    if file and file.filename:
        if not allowed_file(file.filename):
            request.session['flash_error']="Only PDF files are allowed for upload."
            return RedirectResponse(url='/my_submissions',status_code=303)
        
        folder_name='students_assignments' if type=='assignment' else 'students_quizes'
        upload_path=os.path.join(os.getcwd(),'static','uploads','students_uploads',folder_name)
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        filename=secure_filename(f"SID: {student_id}_{timestamp}_{file.filename}")
        full_filepath=os.path.join(upload_path,filename)
        contents=file.file.read()
        with open(full_filepath,'wb')as f:
            f.write(contents)
        db_file_path=f"uploads/students_uploads/{folder_name}/{filename}"
        try:
            StudentModel.insert_submission(student_id,course_id,section_id,db_file_path,type)
        except Exception as e:
            print(f"Error during upload submissions: {str(e)}")
            return templates.TemplateResponse(request=request,name="my_submissions.html",
                                              context={"error":"Error.. Try after a while"})    

    request.session['flash_success']=f"{filename} uploaded successfully!"
    return RedirectResponse(url='/my_submissions',status_code=303)            








