from fastapi import APIRouter,Depends,Request,UploadFile,File,Form,status
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from datetime import datetime
from pathlib import Path
import bleach
from students_module.schema import *
from students_module.services.student_services import StudentService
from students_module.students_models import StudentModel
from utils.auth import get_current_student
from utils.exceptions import BusinessRuleError,ValidationError as AppValidation,NotFoundError
import logging
import secrets
from utils.csrf import verify_csrf,get_csrf_token


router=APIRouter(dependencies=[Depends(verify_csrf)])
base_dir=Path(__file__).parent.parent
templates=Jinja2Templates(directory=[str(base_dir/"students_module" / "students_views"),str(base_dir/"templates")])
templates.env.globals["csrf_token"]=get_csrf_token




@router.get('/student_login',response_class=HTMLResponse)
@router.post('/student_login',response_class=HTMLResponse)
def student_login(request:Request,email:str=Form(None),password:str=Form(None),remember_me:bool=Form(False)):
    if request.method=="GET":
        return templates.TemplateResponse(request=request,name="student_login.html")

    try:
        inputs=StudentLoginRequest(
            email=email,
            password=password,
            remember_me=remember_me
        )
        user,student_obj=StudentService.authenticate_student(inputs.email,inputs.password)
        request.session.update({
            'user_id':user['user_id'],
            'role':'student',
            'student_id':student_obj['student_id'],
            'date':datetime.now().isoformat(),
            'remember':inputs.remember_me
        })
        return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
    except (ValidationError,BusinessRuleError,NotFoundError) as e:
        logging.warning(f"Validation/Business error during login route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_login.html",
                                context={"error":"Invalid Credentials" if isinstance(e,BusinessRuleError) else "Format Invalid"})


@router.get('/student_base')
def student_base(request:Request,current_user:dict=Depends(get_current_student)):
    user_id=current_user['user_id']
    try:
        student_name=StudentModel.get_student_name_by_user_id(user_id)
        return templates.TemplateResponse(request=request,name="student_base.html",context={"student_name":student_name})
    except Exception as e:
        logging.exception(f"Error during student base api: {str(e)}")
        return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/student_profile')
def student_profile(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        student_obj=StudentModel.get_student_by_id(student_id)
        program=StudentModel.get_student_program_details(student_id)
        return templates.TemplateResponse(request=request,name="student_profile.html",
                                          context={"student_obj":student_obj,"program":program})
    except Exception as e:
        logging.exception(f"Error during student profile route api: {str(e)}")
        return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/student_dashboard')
def student_dashboard(request:Request,current_user:dict=Depends(get_current_student)):
    user_id=current_user['user_id']
    student_id=current_user['student_id']
    try:
        dashboard_data=StudentService.get_dashboard_data(student_id,user_id)

        dashboard_data['flash_success']=request.session.pop('flash_success',None)
        dashboard_data['flash_error']=request.session.pop('flash_error',None)

        if dashboard_data.get("access_denied"):
            return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                              context=dashboard_data)
        
        return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                            context=dashboard_data)
    except Exception as e:
        logging.exception(f"Error during student dashboard route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                          context={"error":"Try again"})


@router.get('/student_fee')
def student_fee(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        fee_record=StudentModel.get_student_fee_records(student_id)
        records=[]
        for row in fee_record:
            records.append(
                FeeRecordHelper(
                    program=str(row.get('program')),
                    month=str(row.get('month')),
                    fee_amount=float(row.get('fee_amount')),
                    paid_date=row.get('paid_date'),
                    status=str(row.get('status')),
                    front_voucher=str(row.get('front_voucher')),
                    back_voucher=str(row.get('back_voucher'))
                )
            )
        # records=[FeeRecordHelper(program=str(row['program']),month=str(row['month'] or 'N/A'),fee_amount=float(row['fee_amount']),paid_date=row['paid_date'],status=str(row['status']),front_voucher=row['front_voucher'] or '',back_voucher=row['back_voucher'] or '') for row in fee_record]
        return templates.TemplateResponse(request=request,name="student_fee.html",
                                          context={"fee_records":records})
    except Exception as e:
        logging.exception(f"Error during student fee route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_fee.html",
                                          context={"error":"Error loading fee records"})



@router.get('/complaint_suggestion')
@router.post('/complaint_suggestion')
def complaint_suggestion(request:Request,title:str=Form(None),description:str=Form(None),current_user:dict=Depends(get_current_student)):
    user_id=current_user['user_id']

    if request.method=='GET':
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html")
    
    try:
        inputs=ComplaintSuggestionRequest(title=title,description=description)
        StudentModel.insert_complaint_suggestion(bleach.clean(inputs.title,tags=[]),bleach.clean(inputs.description,tags=[]),user_id)
        request.session['flash_success']="Complaint/Suggestion submitted successfully"
        return RedirectResponse(url='/notifications',status_code=status.HTTP_303_SEE_OTHER)
    
    except ValidationError as v:
        logging.warning(f"Error during complnt suggstn route api: {str(v)}")
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html",
                                          context={"error_msg":"Length error"})
    
    except Exception as e:
        logging.exception(f"Error during complnt suggstn route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html",
                                          context={"error":"Failed"})



@router.get('/notifications')
def notifications(request:Request,current_user:dict=Depends(get_current_student)):
    user_id=current_user['user_id']
    try:
        try:
            complaint_status=StudentModel.get_complaint_status(user_id)
        except ValueError:
            complaint_status=[]

        return templates.TemplateResponse(request=request,name="notifications.html",
                                          context={'complaint_status':complaint_status,
                                                   'msg':request.session.get('flash_success')})
    
    except Exception as e:
        logging.exception(f"Error during notification route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_dashboard.html")



@router.get('/upload_fee')
@router.post('/upload_fee')
def upload_fee(request:Request,month:str=Form(None),fee_amount:float=Form(None),
               front_voucher:UploadFile=File(None),back_voucher:UploadFile=File(None),
               current_user:dict=Depends(get_current_student)):
    
    student_id=current_user['student_id']
               
    if request.method=='GET':
        return templates.TemplateResponse(request=request,name="upload_fee.html")
    
    try:
        inputs=UploadFeeVoucherRequest(
            month=month,
            fee_amount=fee_amount
            )
        
        if not front_voucher or not back_voucher:
            logging.warning(f"Error during upload fee route api: {student_id}")
            raise AppValidation("Both vouchers required")
        
        StudentService.upload_fee_voucher(student_id,inputs.month,inputs.fee_amount,front_voucher,back_voucher)
        request.session['flash_success']="Fee voucher uploaded successfully"
        return RedirectResponse(url='/student_fee',status_code=status.HTTP_303_SEE_OTHER)
    
    except (ValidationError,AppValidation) as e:
        logging.warning(f"Error during upload fee validation route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="upload_fee.html",context={"error":str(e)})
    except Exception as e:
        logging.exception(f"Error during upload fee route api: {str(e)}")
        request.session['flash_error']="Kindly try again"
        return RedirectResponse(url='/student_fee',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/view_attendence')
def view_attendence(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']

    try:
        report=StudentService.get_attendance_data(student_id)
        if not report:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                              context={"message":"No course found"})
        
        return templates.TemplateResponse(request=request,name="view_attendence.html",
                                          context={"attendance_report":report})
    
    except Exception as e:
        logging.exception(f"Error during view attndnc route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_login.html",
                                          context={"error":"Login Again"})



@router.get('/view_grades')
def view_grades(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        details=StudentModel.get_student_by_id(student_id)
        marks=StudentModel.get_student_results_with_marks(student_id)
        if not marks:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                              context={"message":"No grades found"})
        
        marks_objs=[GradeHelper(**row) for row in marks]
        return templates.TemplateResponse(request=request,name="view_grades.html",
                                          context={
                                              "student_details":details,
                                              "all_marks": marks_objs
                                              })
    
    except Exception as e:
        logging.exception(f"Error during view grades route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_login.html",
                                          context={"error":"Login Again"})




@router.get('/course_registeration')
def course_registeration(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        student=StudentModel.get_student_by_id(student_id)
        if str(StudentModel.get_system_setting('is_course_reg_open')) != '1':
            return templates.TemplateResponse(request=request,name="course_registeration.html",
                                              context={
                                                  "student":student,
                                                  "reg_closed":True, 
                                                  "selected":[], 
                                                  "can_register":False
                                                  })
        
        selected=list(StudentModel.get_improvement_subjects(student_id) or []) + list(StudentModel.get_retake_subjects(student_id) or [])
        return templates.TemplateResponse(request=request,name="course_registeration.html",
                                          context={
                                              "student":student,
                                              "selected":selected,
                                              "reg_closed":False,
                                              "can_register":True,
                                              "flash_success":request.session.pop('flash_success',None),
                                              "flash_error":request.session.pop('flash_error',None)
                                              })
    
    except Exception as e:
        logging.exception(f"Error during course rgstrtn route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="course_registeration.html",
                                          context={"error":"Try Again"})



@router.get('/improvement_subject')
def improvement_subject(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        if StudentModel.get_existing_improvement_request(student_id):
            request.session['flash_error']="Only one subject for improvement"
            return RedirectResponse(url='/course_registeration',status_code=status.HTTP_303_SEE_OTHER)

        
        smstr_pass=StudentModel.get_max_semester_passed(student_id)
        courses=StudentModel.get_eligible_improvement_courses(student_id,smstr_pass)
        return templates.TemplateResponse(request=request,name="improvement_subject.html",
                                          context={"courses":courses})
    
    except Exception as e:
        logging.exception(f"Error during imprvmnt subj route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="course_registeration.html",
                                          context={"error":"Try Again"})



@router.post('/delete_improvement/{improvement_id}')
def delete_improvement(request:Request,improvement_id:int,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']

    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        StudentModel.delete_improvement_subject(improvement_id,student_id)
        request.session['flash_success']="Improvement subject deleted"

    except Exception as e:
        logging.exception(f"Error during dlt imprvmnt route api: {str(e)}")
        request.session['flash_error']="Try again!"

    return RedirectResponse(url='/course_registeration',status_code=status.HTTP_303_SEE_OTHER)



@router.post('/select_improvement/{course_id}')
def select_improvement(request:Request,course_id:int,form_course_id:int=Form(None),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    user_id=current_user['user_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)

        
        StudentService.handle_improvement_request(student_id,user_id,form_course_id or course_id)
        request.session['flash_success']="Improvement requested!"
    except Exception as e:
        logging.exception(f"Error during slct imprvmnt route api: {str(e)}")
        request.session['flash_error']="Try again"

    return RedirectResponse(url='/course_registeration',status_code=status.HTTP_303_SEE_OTHER)



@router.get('/help_desk')
@router.post('/help_desk')
def help_desk(request:Request):
    try:
        return templates.TemplateResponse(request=request, name="help_desk.html")
    except Exception as e:
        logging.exception(f"Error during student profile route api: {str(e)}")
        return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/fail_subjects')
def fail_subjects(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        if StudentModel.get_existing_retake_request(student_id):
            request.session['flash_error']="Only one subject for retake"
            return RedirectResponse(url='/course_registeration',status_code=status.HTTP_303_SEE_OTHER)

        smstr_pass=StudentModel.get_max_semester_passed(student_id)
        fail_courses=StudentModel.get_eligible_fail_subjects(student_id,smstr_pass)
        return templates.TemplateResponse(request=request,name="fail_subjects.html",context={"courses":fail_courses})
    
    except Exception as e:
        logging.exception(f"Error during fail subjs route api: {str(e)}")
        return RedirectResponse(url='/course_registeration',status_code=status.HTTP_303_SEE_OTHER)



@router.post('/select_fail/{course_id}')
def select_fail(request:Request,course_id:int,form_course_id:int=Form(None),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    user_id=current_user['user_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        StudentService.handle_fail_subject_request(student_id,user_id,form_course_id or course_id)
        request.session['flash_success']="Retake request successfully!"

    except Exception as e:
        logging.exception(f"Error during slsct fail route api: {str(e)}")
        request.session['flash_error']="Try again"

    return RedirectResponse(url='/course_registeration',status_code=status.HTTP_303_SEE_OTHER)



@router.post('/delete_fail/{fail_id}')
def delete_fail(request:Request,fail_id:int,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        StudentModel.delete_fail_subject(fail_id,student_id)
        request.session['flash_success']="Retake removed"

    except Exception as e:
        logging.exception(f"Error during dlt fail route api: {str(e)}")
        request.session['flash_error']="Failed to remove"

    return RedirectResponse(url='/course_registeration',status_code=status.HTTP_303_SEE_OTHER)



@router.get('/semester_freeze')
@router.post('/semester_freeze')
def semester_freeze(request:Request,reason:str=Form(None),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    
    try:
        student=StudentModel.get_student_by_id(student_id)
        semester=StudentModel.get_last_recorded_semester(student_id)
        
        if request.method=='GET':
            existing=StudentModel.get_active_semester_freeze_request(student_id)
            return templates.TemplateResponse(request=request,name="semester_freeze.html",
                                                        context={
                                                            "existing_request":existing,
                                                            "already_applied":bool(existing),
                                                            "semester":semester,
                                                            "student":student
                                                        })
        
        inputs=SemesterFreezeRequest(reason=reason)
        StudentService.handle_semester_freeze(student_id,inputs.reason)
        request.session['flash_success']="Request submitted"
        return RedirectResponse(url='/semester_freeze', status_code=status.HTTP_303_SEE_OTHER)
    
    except (ValidationError,BusinessRuleError,NotFoundError) as e:
        logging.exception(f"Error during smstr freeze route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="semester_freeze.html",
                                                            context={
                                                                "semester":None,
                                                                "student":None,
                                                                "already_applied":False,
                                                                "error":"Try again"
                                                            })
    except Exception as e:
        logging.exception(f"Error during smstr freeze route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="semester_freeze.html",
                                                                context={
                                                                    "semester":None,
                                                                    "student":None,
                                                                    "already_applied":False,
                                                                    "error":"Try again"
                                                                })



@router.get('/summer_semester')
def summer_semester(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        student=StudentModel.get_student_by_id(student_id)
        if str(StudentModel.get_system_setting('is_summer_app_open')) != '1':
            return templates.TemplateResponse(request=request,name="summer_semester.html",
                                              context={
                                                  "student":student,
                                                  "summer_closed":True,
                                                  "selected":[],
                                                  "can_register":False,
                                                  "failed_count":0
                                                  })
        
        latest=StudentModel.get_latest_summer_semester()
        if not latest:
            return templates.TemplateResponse(request=request,name="summer_semester.html",
                                              context={
                                                  "student":student,
                                                  "summer_closed":True,
                                                  "selected":[],
                                                  "can_register":False,
                                                  "failed_count":0
                                                  })
        
        summer_id=latest['summer_semesters_id']
        selected=StudentModel.get_selected_summer_subjects(student_id,summer_id) if latest else []
        failed=StudentModel.get_eligible_summer_failed_subjects(current_user['student_id']) if latest else []
        return templates.TemplateResponse(request=request,name="summer_semester.html",
                                          context={
                                              "student":student,
                                              "selected":selected,
                                              "can_register":(failed and len(selected) < len(failed) and latest.get('status') == 'Open'),
                                              "failed_count":len(failed),
                                              "latest_summer":latest,
                                              "summer_closed":False
                                              })
    
    except Exception as e:
        logging.exception(f"Error during summer smstr route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_dashboard.html",context={"error":"Try again"})



@router.get('/summer_subjects')
def summer_subjects(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        latest=StudentModel.get_latest_summer_semester()
        if not latest:
            request.session['flash_error']="No summer active"
            return RedirectResponse(url='/summer_semester',status_code=status.HTTP_303_SEE_OTHER)

        summer_id=latest['summer_semesters_id']
        selected_ids=[s['course_id'] for s in StudentModel.get_selected_summer_subjects(student_id,summer_id)]
        return templates.TemplateResponse(request=request,name="summer_subjects.html",
                                          context={
                                              "subjects":[sub for sub in StudentModel.get_eligible_summer_failed_subjects(student_id) if sub['course_id'] not in selected_ids]})
   
    except Exception as e:
        logging.exception(f"Error during summr subjs route api: {str(e)}")
        return RedirectResponse(url='/summer_semester',status_code=status.HTTP_303_SEE_OTHER)



@router.post('/select_summer_subject/{subject_id}')
def select_summer_subject(request:Request,subject_id:int,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        StudentService.handle_summer_registration(student_id,subject_id)
        request.session['flash_success']="Subject added"
    except Exception as e:
        logging.exception(f"Error during slct summr subjs route api: {str(e)}")
        request.session['flash_error']="Try again"

    return RedirectResponse(url='/summer_semester',status_code=status.HTTP_303_SEE_OTHER)



@router.post('/delete_summer_subject/{subject_id}')
def delete_summer_subject(request:Request,subject_id:int,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        latest=StudentModel.get_latest_summer_semester()
        if not latest:
            request.session['flash_error']="No summer semester available"
            return RedirectResponse(url='/summer_semester',status_code=status.HTTP_303_SEE_OTHER)
        
        summer_id=latest['summer_semesters_id']
        StudentModel.delete_summer_subject(student_id,subject_id,summer_id)
        request.session['flash_success']="Subject removed"

    except Exception as e:
        logging.exception(f"Error during dlt summr subjs route api: {str(e)}")
        request.session['flash_error']="Try again"

    return RedirectResponse(url='/summer_semester',status_code=status.HTTP_303_SEE_OTHER)



@router.get('/student_fyp')
def student_fyp(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        StudentService.check_fyp_semester(student_id)
        student=StudentModel.get_student_by_id(student_id)
        fyp=StudentModel.get_fyp_project(student_id)
        messages=StudentModel.get_fyp_messages(fyp['fyp_id']) if fyp else []
        teacher=StudentModel.get_teacher_full_details(fyp['teacher_id']) if fyp and fyp.get('teacher_id') else None
        all_teachers=StudentModel.get_all_teachers()
        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)
        return templates.TemplateResponse(request=request,name="student_fyp.html",
                                          context={
                                              "student":student,
                                              "fyp":fyp,
                                              "messages":messages,
                                              "teacher":teacher,
                                              "all_teachers":all_teachers,
                                              "flash_success":flash_success,
                                              "flash_error":flash_error
                                              })
    except (BusinessRuleError,AppValidation,NotFoundError) as ee:
        logging.warning(f"Error during student fyp route api: {str(ee)}")
        request.session['flash_error']=str(ee)
        return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
    
    except Exception as e:
        logging.exception(f"Error during student fyp route api: {str(e)}")
        return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)




@router.post('/submit_fyp')
def submit_fyp(request:Request,project_title:str=Form(...),description:str=Form(...),teacher_id:int=Form(None),
               proposal_file:UploadFile=File(None),current_user:dict=Depends(get_current_student)):
    
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        StudentService.submit_fyp_proposal(student_id,project_title,description,teacher_id,proposal_file)
        request.session['flash_success']="FYP proposal submitted"
    except (BusinessRuleError,AppValidation,NotFoundError) as ee:
        logging.warning(f"Error during submit fyp route api: {str(ee)}")
        request.session['flash_error']=str(ee)    
    except Exception as e:
        logging.exception(f"Error during submit fyp route api: {str(e)}")
        request.session['flash_error']="Try again"

    return RedirectResponse(url='/student_fyp',status_code=status.HTTP_303_SEE_OTHER)





@router.post('/send_fyp_message/{fyp_id}')
def send_fyp_message(request:Request,fyp_id:int,message:str=Form(...),current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        fyp_obj=StudentModel.get_fyp_by_id_and_student(fyp_id,student_id)
        if fyp_obj and message.strip():
            StudentModel.insert_fyp_message(fyp_id,student_id,'student',message.strip())
    except Exception as e:
        logging.exception(f"Error during send fyp msg route api: {str(e)}")
        pass

    return RedirectResponse(url='/student_fyp',status_code=status.HTTP_303_SEE_OTHER)



@router.post('/update_fyp')
def update_fyp(request:Request,project_title:str=Form(...),
               proposal_file:UploadFile=File(None),current_user:dict=Depends(get_current_student)):
    
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        StudentService.update_fyp(student_id,project_title,proposal_file)
        request.session['flash_success']="FYP updated"
    except (BusinessRuleError,AppValidation,NotFoundError) as ee:
        logging.warning(f"Error during update fyp route api: {str(ee)}")
        request.session['flash_error']=str(ee)
    except Exception as e:
        logging.exception(f"Error during updt fyp route api: {str(e)}")
        request.session['flash_error']="Try again"
    return RedirectResponse(url='/student_fyp',status_code=status.HTTP_303_SEE_OTHER)        



@router.get('/my_submissions')
def my_submissions(request:Request,current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        courses=StudentModel.get_enrolled_courses_by_student_id(student_id)
        if not courses:
            return templates.TemplateResponse(request=request,name="student_dashboard.html",
                                              context={"message":"No course found"})
        
        course_ids=[c['course_id'] for c in courses]
        course_names={
            c['course_id']:c['course_name'] 
            for c in StudentModel.get_course_details_by_ids(course_ids)
        }

        schedule=StudentModel.get_course_schedule_for_enrolled_sections(course_ids,student_id)
        
        for s in schedule: 
            s['course_name']=course_names.get(s['course_id'])
            
        submissions=StudentModel.get_student_submission_status(student_id)
        a_marks={}
        q_marks={}
        a_totals={}
        q_totals={}
        for sub in submissions:
            cid=int(sub['course_id'])
            
            if sub['submission_type']=='assignment':
                a_marks[cid]=sub['marks']
                a_totals[cid]=sub['total_marks']
            elif sub['submission_type']=='quiz':
                q_marks[cid]=sub['marks']
                q_totals[cid]=sub['total_marks']

        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)       
        return templates.TemplateResponse(request=request,name="my_submissions.html",
                                                        context={
                                                                'schedule':schedule,
                                                                'uploaded_assignments':list(a_marks.keys()),
                                                                'assignment_marks':a_marks,
                                                                'uploaded_quizzes':list(q_marks.keys()),
                                                                'quiz_marks':q_marks,
                                                                'assignment_totals':a_totals,
                                                                'quiz_totals':q_totals,
                                                                'flash_success':flash_success,
                                                                'flash_error':flash_error})
        
    except Exception as e:
        logging.exception(f"Error during my submissions route api: {str(e)}")
        return templates.TemplateResponse(request=request,name="student_dashboard.html",context={"error":"Try again"})




@router.post('/upload_submission')
def upload_submission(request:Request,course_id:int=Form(...),section_id:int=Form(...),type:str=Form(...),
                      file:UploadFile=File(...), current_user:dict=Depends(get_current_student)):
    student_id=current_user['student_id']
    try:
        check_status=StudentService.check_freeze_student(student_id)
        if check_status:
            request.session['flash_error']="Your semester has been freeze"
            return RedirectResponse(url='/student_dashboard',status_code=status.HTTP_303_SEE_OTHER)
        
        filename=StudentService.upload_assignment_quiz(student_id,course_id,section_id,type,file)
        request.session['flash_success']=f"{filename} uploaded successfully!"
    except Exception as e:
        logging.exception(f"Error during upld submissions route api: {str(e)}")
        request.session['flash_error']="Try again"

    return RedirectResponse(url='/my_submissions',status_code=status.HTTP_303_SEE_OTHER)
