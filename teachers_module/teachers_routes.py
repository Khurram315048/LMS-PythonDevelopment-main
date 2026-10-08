import pathlib
from fastapi import APIRouter,Depends,Request,Form,status,Path
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pydantic import ValidationError as PydanticValidationError
import logging
from utils.auth import get_current_teacher
from utils.exceptions import BusinessRuleError,ValidationError,NotFoundError
from teachers_module.services.teacher_services  import TeacherService
from teachers_module.teachers_models import TeacherModel
from teachers_module.schema import (TeacherLoginRequest,AttendanceForm,SendMessageForm,MarkSubmissionForm,ComplaintSuggestionForm,subType,subStatus,FypStatus)
from utils.csrf import verify_csrf,get_csrf_token


router=APIRouter(dependencies=[Depends(verify_csrf)])
base_dir=pathlib.Path(__file__).parent.parent
templates=Jinja2Templates(directory=[str(base_dir / "teachers_module" / "teachers_views"),str(base_dir / "templates")])
templates.env.globals["csrf_token"]=get_csrf_token

@router.get('/teacher_login',response_class=HTMLResponse)
@router.post('/teacher_login',response_class=HTMLResponse)
def teacher_login(request:Request,email:str=Form(None),password:str=Form(None),remember_me:bool=Form(False)):
    if request.method=="GET":
        return templates.TemplateResponse(request=request,name="teacher_login.html")

    try:
        if not email or not password:
            raise ValidationError("Email and Password are required.")

        inputs=TeacherLoginRequest(
            email=email,
            password=password,
            remember_me=remember_me
        )   
        user,teacher_obj=TeacherService.authenticate_teacher(inputs.email,inputs.password)
        
        request.session.update({
            'user_id':user['user_id'],
            'role':'teacher',
            'teacher_id':teacher_obj['teacher_id'],
            'date':datetime.now().isoformat(),
            'remember':remember_me
        })
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)
    except PydanticValidationError as ve:
        logging.error(f"Error during pydntvl tchr lgn route api: {str(ve)}")
        return templates.TemplateResponse(request=request,name="teacher_login.html",
                                          context={"error":str(ve)})
    except (ValidationError,BusinessRuleError,NotFoundError) as e:
        logging.warning(f"Error during teacher login: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_login.html",context={"error":str(e)})
    except Exception as e:
        logging.exception(f"Error during tcher login route: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_login.html",
                                          context={"error":"Please try again."})



@router.get('/teacher_dashboard')
def teacher_dashboard(request:Request,current_user:dict=Depends(get_current_teacher)):
    user_id=current_user['user_id']
    teacher_id=current_user['teacher_id']
    try:
        dashboard_data=TeacherService.teacher_dashboard(user_id,teacher_id)
        dashboard_data['flash_success']=request.session.pop('flash_success',None)
        dashboard_data['flash_error']=request.session.pop('flash_error',None)
        
        return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                          context=dashboard_data)
    
    except (BusinessRuleError,NotFoundError) as bn:
        logging.warning(f"Error during tchr dashbr route: {str(bn)}")
        request.session['flash_error']=str(bn)
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)  
    except Exception as e:
        logging.exception(f"Error during tcher dshbrd route: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_login.html",
                                          context={"error":"Try again later."})



@router.get('/teacher_profile')
def teacher_profile(request:Request,current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        details=TeacherModel.get_profile(teacher_id)
        if not details:
            raise NotFoundError("No record found")

        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)
        return templates.TemplateResponse(request=request,name="teacher_profile.html",
            context={
                "details":details,
                "flash_error":flash_error,
                "flash_success":flash_success
                })
    except (NotFoundError) as n:
            logging.warning(f"Error during tchr prfl route: {str(n)}")
            request.session['flash_error']=str(n)
            return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during tchr prfl route: {str(e)}")
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)    

        

@router.get('/class_attendance')
def class_attendance(request:Request,current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        data=TeacherService.class_attendance(teacher_id)
        data['flash_success']=request.session.pop('flash_success',None)
        data['flash_error']=request.session.pop('flash_error',None)
        return templates.TemplateResponse(request=request,name="class_attendance.html",context=data)
    
    except (BusinessRuleError,NotFoundError) as bn:
            logging.warning(f"Error during cls attndnc route: {str(bn)}")
            request.session['flash_error']=str(bn)
            return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during cls atndnc route: {str(e)}")
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/class_structure/{section_id}')
def class_structure(request:Request,section_id:int,current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        structure=TeacherService.get_class_details(teacher_id,section_id)
        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)
        
        return templates.TemplateResponse(request=request,name="class_structure.html",
        context={
            "class_info":structure, 
            "section_id":section_id,
            "flash_success":flash_success,
            "flash_error":flash_error
        })
    except (BusinessRuleError,NotFoundError) as e:
        logging.warning(f"Error accessing clss strcte: {str(e)}")
        request.session['flash_error']=str(e)
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during cls stctre route: {str(e)}")
        request.session['flash_error']="Try again later."
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/marked_attendance/{section_id}')
def marked_attendance_get(request:Request,section_id:int,current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        data=TeacherService.prepare_attendance_data(teacher_id,section_id)
        data['section_id']=section_id
        data['flash_success']=request.session.pop('flash_success',None)
        data['flash_error']=request.session.pop('flash_error',None)
        return templates.TemplateResponse(request=request,name="marked_attendance.html",context=data)
    
    except (BusinessRuleError,NotFoundError) as bn:
        logging.warning(f"Error during mrkd attnd route api: {str(bn)}")
        request.session['flash_error']=str(bn)
        return RedirectResponse(url='/class_attendance',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during mrkd attndc get route api: {str(e)}")
        request.session['flash_error']="System error"
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)


@router.post('/marked_attendance/{section_id}')
async def marked_attendance_post(request:Request,section_id:int=Path(...,gt=0),attendance_date:str=Form(...),
                                 current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        form_data=dict(await request.form())
        records={}
        for k,v in form_data.items():
            if k.startswith('status'):
                try:
                    records[int(k.split('_',1)[1])]=v
                except ValueError:
                    continue

        AttendanceForm(
            attendance_date=attendance_date,
            status_record=records
        )
        TeacherService.submit_attendance(teacher_id,section_id,attendance_date,form_data)
        request.session['flash_success']="Attendance marked successfully."
        return RedirectResponse(url='/class_attendance',status_code=status.HTTP_303_SEE_OTHER)
    except PydanticValidationError as ve:
        logging.error(f"Error during pdyntval mark attndc pst route api: {str(ve)}")
        request.session['flash_error']=str(ve)
        return RedirectResponse(url=f'/marked_attendance/{section_id}',status_code=status.HTTP_303_SEE_OTHER)
    except (BusinessRuleError,ValidationError) as e:
        logging.warning(f"Error during mrkd attnd post route: {str(e)}")
        request.session['flash_error']=str(e)
        return RedirectResponse(url=f'/marked_attendance/{section_id}',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during mrkd attnd post route api: {str(e)}")
        request.session['flash_error']="System error"
        return RedirectResponse(url=f'/marked_attendance/{section_id}',status_code=status.HTTP_303_SEE_OTHER)




@router.post('/toggle_upload/{section_id}/{upload_type}')
def toggle_upload(request:Request,section_id:int=Path(...,gt=0),upload_type:subType=Path(...),current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        TeacherService.toggle_upload_status(teacher_id,section_id,upload_type)
        request.session['flash_success']=f"{upload_type.capitalize()} status updated."
    except(BusinessRuleError,ValidationError) as v:
        logging.warning(f"Error during uplod wraning: {str(v)}")
        request.session['flash_error']=str(v)    
    except Exception as e:
        logging.exception(f"Error during tgl uplo route api: {str(e)}")

    return RedirectResponse(url=f'/class_structure/{section_id}',status_code=status.HTTP_303_SEE_OTHER)



@router.get('/generate_result/{section_id}')
def generate_result_get(request:Request,section_id:int,current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        students_data,meta=TeacherService.get_generate_result_data(teacher_id,section_id)
        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)
        return templates.TemplateResponse(request=request,name="generate_result.html",
                                          context={
                                                "students":students_data,
                                                "info":meta,
                                                "flash_success":flash_success,
                                                "flash_error":flash_error
                                            })
    except BusinessRuleError as b:
        logging.warning(f"warning during gnrt rst gpa: {str(b)}")
        request.session['flash_error']=str(b)
        return RedirectResponse(url=f'/class_structure/{section_id}',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during gnrt rslt route api: {str(e)}")
        request.session['flash_error']="Try again"
        return RedirectResponse(url=f'/class_structure/{section_id}',status_code=status.HTTP_303_SEE_OTHER)



@router.post('/generate_result/{section_id}')
async def generate_result_post(request:Request,section_id:int,current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        form_data=dict(await request.form())
        TeacherService.submit_bulk_results(teacher_id,section_id,form_data)
        request.session['flash_success']="Results uploaded successfully!"
    except (BusinessRuleError,ValidationError) as bv:
        logging.warning(f"Warning during gnrt rst post route: {str(bv)}")
        request.session['flash_error']=str(bv)    
        return RedirectResponse(url=f'/generate_result/{section_id}',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during gnrt pst route api: {str(e)}")
        request.session['flash_error']=str(e) 
    return RedirectResponse(url=f'/generate_result/{section_id}',status_code=status.HTTP_303_SEE_OTHER)



@router.get('/fyp_management')
def fyp_management(request:Request,current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        groups=TeacherService.get_fyp_groups_data(teacher_id)
        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)
        completed_fyp=0
        pending_fyp=0
        for g in groups:
            if g['status']=='Completed':
                completed_fyp+=1
            elif g['status']=='In Progress':
                pending_fyp+=1    

        
        return templates.TemplateResponse(request=request,name="fyp_management.html",
                                          context={
                                            "fyp_data":groups,
                                            "total":len(groups),
                                            "completed":completed_fyp,
                                            "pending":pending_fyp,
                                            "flash_success":flash_success,
                                            "flash_error":flash_error
                                        })
    except (NotFoundError,BusinessRuleError) as nb:
        logging.warning(f"Error during fyp mngmnt route: {str(nb)}")
        request.session['flash_error']=str(nb)
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during fyp mngmnt route: {str(e)}")
        request.session['flash_error']="System error"
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/approve_fyp/{fyp_id}/{status_val}')
def approve_fyp(request:Request,fyp_id:int=Path(...,gt=0),status_val:FypStatus=Path(...),current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        TeacherService.manage_fyp_status(teacher_id,fyp_id,status_val)
        request.session['flash_success']=f"FYP {status_val} successfully."
    except (BusinessRuleError,ValidationError,NotFoundError) as bvn:
        logging.warning(f"Error during aprv fyp route: {str(bvn)}")
        request.session['flash_error']=str(bvn)
        return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)    
    except Exception as e:
        logging.exception(f"Error during aprv fyp route: {str(e)}")
        request.session['flash_error']=str(e)
    return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)


@router.post('/send_message/{fyp_id}')
def send_message(request:Request,fyp_id:int=Path(...,gt=0),message:str=Form(...),current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        valid_data=SendMessageForm(
            message=message
        )
        TeacherService.send_fyp_message(teacher_id,fyp_id,valid_data.message)
    except PydanticValidationError as ve:
        request.session['flash_error']=str(ve)
    except (BusinessRuleError,ValidationError) as bv:
        logging.warning(f"Error during snd msg route: {str(bv)}")
        request.session['flash_error']=str(bv)   
    except Exception as e:
        logging.exception(f"Error during snd msg route api: {str(e)}")
        request.session['flash_error']="System error"
    return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)




@router.get('/view_submissions/{section_id}/{sub_type}')
def view_submissions(request:Request,section_id:int=Path(...,gt=0),sub_type:subType=Path(...),current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        subs,meta=TeacherService.get_submissions(teacher_id,section_id,sub_type)
        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)

        return templates.TemplateResponse(request=request,name="view_submissions.html",
                                          context={
                                        "submissions":subs,
                                        "course_name":meta['course_name'] if meta else "",
                                        "section_id":section_id,
                                        "sub_type":sub_type,
                                        "flash_success":flash_success,
                                        "flash_error":flash_error
                                    })
    except (BusinessRuleError,NotFoundError) as bn:
        logging.warning(f"Error during vw subms route: {str(bn)}")
        request.session['flash_error']=str(bn)
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"Error during vw submsn route api: {str(e)}")
        request.session['flash_error']="System error"
        return RedirectResponse(url=f'/class_structure/{section_id}',status_code=status.HTTP_303_SEE_OTHER)


@router.post('/mark_submission/{submission_id}')
def mark_submission(request:Request,submission_id:int=Path(...,gt=0),section_id:int=Form(...),sub_type:subType=Form(...),
                    marks:float=Form(...),total_marks:float=Form(...),current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        valid_inputs=MarkSubmissionForm(
            marks=marks,
            total_marks=total_marks,
            section_id=section_id,
            sub_type=sub_type
        )
        TeacherService.grade_submission(teacher_id,valid_inputs.section_id,submission_id,valid_inputs.marks,valid_inputs.total_marks,valid_inputs.sub_type)
        request.session['flash_success']="Grades updated successfully."
    except PydanticValidationError as ve:
        request.session['flash_error']=str(ve)    
    except (BusinessRuleError,ValidationError) as bv:
        logging.warning(f"Error during mrk submsn route: {str(bv)}")
        request.session['flash_error']=str(bv)
    except Exception as e:
        logging.exception(f"Error during mrk submsn route api: {str(e)}")
        request.session['flash_error']="System error"
    return RedirectResponse(url=f'/view_submissions/{section_id}/{sub_type}',status_code=status.HTTP_303_SEE_OTHER)


@router.post('/set_submission_status/{submission_id}/{status_val}')
@router.post('/set_submission/{submission_id}/{status_val}') 
def set_submission_status(request:Request,submission_id:int=Path(...,gt=0),status_val:subStatus=Path(...),
                          section_id:int=Form(...),sub_type:subType=Form(...),current_user:dict=Depends(get_current_teacher)):
    teacher_id=current_user['teacher_id']
    try:
        TeacherService.set_submission_status(teacher_id,section_id,submission_id,status_val)
        request.session['flash_success']=f"Status set to {status_val}"
    except (BusinessRuleError,ValidationError) as bv:
        logging.warning(f"Error during st sbmsn route api: {str(bv)}")
        request.session['flash_error']=str(bv)
        return RedirectResponse(url=f'/view_submissions/{section_id}/{sub_type}',status_code=status.HTTP_303_SEE_OTHER)    
    except Exception as e:
        request.session['flash_error']=str(e)
    return RedirectResponse(url=f'/view_submissions/{section_id}/{sub_type}',status_code=status.HTTP_303_SEE_OTHER)


@router.get('/teacher_complaint')
@router.post('/teacher_complaint')
def teacher_complaint(request:Request,title:str=Form(None),description:str=Form(None),current_user:dict=Depends(get_current_teacher)):
    user_id=current_user['user_id']

    
    if request.method=='GET':
        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)
        return templates.TemplateResponse(request=request,name="teacher_complaint.html",
                                          context={
                                              "flash_success":flash_success,
                                              "flash_error":flash_error
                                              })
        
    try:
        take_inputs=ComplaintSuggestionForm(
            title=title,
            description=description
        )
        TeacherService.submit_complaint(user_id,take_inputs.title,take_inputs.description)
        request.session['flash_success']="Complaint/Suggestion submitted successfully."
        return RedirectResponse(url='/teacher_complaint',status_code=status.HTTP_303_SEE_OTHER)
    except PydanticValidationError as ve:
        logging.error(f"Error during tchr cpmlnt route api: {str(ve)}")
        request.session['flash_error']=str(ve)    
    except ValidationError as v:
        logging.warning(f"Validation error on complnt submson: {str(v)}")
        return templates.TemplateResponse(request=request,name="teacher_complaint.html",
                                          context={"flash_error":str(v)})
    except Exception as e:
        logging.exception(f"System error on complnt submsin: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_complaint.html",
                                          context={"flash_error":"System error"})