from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from utils.auth import login_required ,teacher_required
from .teachers_models import TeacherModel,Notifications,ActivityModel
import datetime
import MySQLdb.cursors
from utils.db import mysql
from fastapi import APIRouter,Request,UploadFile,File,Form,status
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from pathlib import Path
from teachers_module.schema import *


teacher_router=APIRouter()
base_dir=Path(__file__).parent.parent
templates=Jinja2Templates(directory=[str(base_dir/"teachers_module"/"teachers_views"),str(base_dir/"templates")])


teacher =Blueprint('teacher', __name__, template_folder='teachers_views')

# @teacher.before_request
# def track_student_activity():
#     teacher_id=session.get('teacher_id')
#     if not teacher_id:
#         return
    
#     if request.path.startswith('/static'):
#         return
    
#     log_id=session.pop('current_log_id',None)

#     if log_id:
#         ActivityModel.log_exit(log_id)

#     new_log_id=ActivityModel.log_enter(
#         teacher_id=teacher_id,
#         page_name=request.endpoint or request.path,
#         page_url=request.path,
#         ip_address=request.remote_addr
#     )
#     session['current_log_id']=new_log_id


# @teacher.route('/track_exit',methods=['POST'])
# def track_exit():
#     log_id=session.pop('current_log_id',None)

#     if log_id:
#         ActivityModel.log_exit(log_id)
#     return '',204


@teacher_router.get('/teacher_login',response_class=HTMLResponse)
@teacher_router.post('/teacher_login',response_class=HTMLResponse)
def teacher_login(request:Request,email:str=Form(None),password:str=Form(None),remember_me:bool=Form(False)):
    if request.method=='GET':
        return templates.TemplateResponse(request=request,name="teacher_login.html")

    try:
        check_inputs=TeacherLoginRequest(
            email=email,
            password=password,
            remember_me=remember_me
        )
    except ValidationError as v:
        print(f"Error inputs: {str(v)}")
        return templates.TemplateResponse(request=request,name="teacher_login.html",
                                          context={"error":"Kindly correct format inputs"},
                                          status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)

    from main import app
    try:
        with app.app_context():
            user_data=TeacherModel.get_by_email(check_inputs.email)
            if not user_data:
                return templates.TemplateResponse(request=request,name="teacher_login.html",
                                                context={"error":"No record found"},status_code=status.HTTP_401_UNAUTHORIZED)

            if user_data['role_id'] != 1:
                return templates.TemplateResponse(request=request,name="teacher_login.html",
                                                  context={"error":"Only Teacher can login"},status_code=status.HTTP_401_UNAUTHORIZED)


            if user_data and check_password_hash(user_data['password'],check_inputs.password):
                user_id=user_data['user_id']
                teacher_obj=TeacherModel.get_by_user_id(user_id)
                if teacher_obj:
                    request.session['user_id']=user_data['user_id']
                    request.session['role']='teacher'
                    request.session['teacher_id']=teacher_obj['teacher_id']
                    request.session['remember_me']=remember_me
                    return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)
                else:
                    return templates.TemplateResponse(request=request,name="teacher_login.html",context={"error":"Record Missing"},
                    status_code=status.HTTP_404_NOT_FOUND)
            else:
                return templates.TemplateResponse(request=request,name="teacher_login.html",context={"error":"Invalid Password"},
                                                  status_code=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(f"Error on teacher login: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_login.html",
                                          context={"error":"Invalid Credentials"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)       

# @teacher.route('/teacher_login',methods=['GET','POST'])
# def teacher_login():
#     try:
#         if request.method=='POST':
#             email=request.form.get('email')
#             password=request.form.get('password')
#             print("Email: ",email)
#             print("Password: ",password)
#             user_data,logged_user=TeacherModel.get_by_email(email)
            
#             if user_data and check_password_hash(logged_user['password'],password):
#                 session.update({
#                     'user_id':logged_user['user_id'], 
#                     'role':'teacher', 
#                     'teacher_id':user_data['teacher_id']
#                 })
#                 return redirect(url_for('teacher.teacher_dashboard'))
#             else:
#                 flash("Invalid email or password","danger")
#                 return redirect(url_for('teacher.teacher_login'))
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return redirect(url_for('teacher.teacher_login'))
            
#     return render_template('teacher_login.html')



# @teacher.route('/teacher_profile')
# @teacher_required
# def teacher_profile():
#     if session.get('role') != 'teacher': 
#         return redirect(url_for('main_view'))
    
#     details=TeacherModel.get_profile(session['teacher_id'])
#     return render_template('teacher_profile.html',teacher_details=details)

@teacher_router.post('/teacher_profile',response_class=HTMLResponse)
@teacher_router.get('/teacher_profile',response_class=HTMLResponse)
def teacher_profile(request:Request):
    teacher_id=request.session.get('teacher_id')
    if request.session.get('role') != 'teacher' and not teacher_id:
        return templates.TemplateResponse(request=request,name="teacher_login.html",
                                          context={"error":"Please login Again"})

    from main import app
    try:
        with app.app_context():
            details=TeacherModel.get_profile(teacher_id)
            if not details:
                return templates.TemplateResponse(request=request,name="teacher_profile.html",
                                                  context={"details":details})

            if request.method=='POST':
                return templates.TemplateResponse(request=request,name="teacher_profile.html",
                context={"details":details,"show_notification":True})
            
            return templates.TemplateResponse(request=request,name="teacher_profile.html",
                                              context={"details":details})
    except Exception as e:
       print(f"Error on teacher profile: {str(e)}")
       return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                         context={"error":"Try Again"})   


# @teacher.route('/teacher_dashboard')
# @teacher_required
# def teacher_dashboard():
#     if session.get('role') != 'teacher':
#         return redirect(url_for('main_view'))
        
#     tid=session.get('teacher_id')
#     today=datetime.datetime.now().strftime('%A')
    
#     full_schedule=TeacherModel.get_full_schedule(tid)
#     today_list=[row for row in full_schedule if row['day_of_week']==today]
    
#     active_notifications=Notifications.get_active_notifications(session['user_id'],'teacher')
#     return render_template('teacher_dashboard.html', 
#                            full_schedule=full_schedule, 
#                            today_schedule=today_list, 
#                            today_name=today,active_notifications=active_notifications)

@teacher_router.get('/teacher_dashboard',response_class=HTMLResponse)
def teacher_dashboard(request:Request):
    if request.session.get('role') != 'teacher':
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_401_UNAUTHORIZED)

    teacher_id=request.session.get('teacher_id')
    user_id=request.session.get('user_id')
    if not teacher_id or not user_id:
        return templates.TemplateResponse(request=request,name="teacher_login.html",
                                          context={"error":"Please Login Again"})

    today=datetime.now().strftime('%A')
    flash_success=request.session.pop('flash_success',None)
    flash_error=request.session.pop('flash_error',None)
    from main import app
    try:
        with app.app_context():
            full_schedule=TeacherModel.get_full_schedule(teacher_id)
            active_notifications=Notifications.get_active_notifications(user_id,'teacher')
            if not full_schedule:
                flash_message='No Schedule Found Yet'
                return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                                  context={"full_schedule":full_schedule,"today_name":today,
                                                           "active_notifications":active_notifications,
                                                           "flash_message":flash_message})
            
            today_list=[row for row in full_schedule if row['day_of_week']==today]
            return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                              context={"today_list":today_list,"full_schedule":full_schedule,"active_notifications":active_notifications,
                                                       "today_name":today,"flash_success":flash_success,"flash_error":flash_error})
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Teacher dashboard error: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                          context={"error":"Loging Again"})
    

# @teacher.route("/class_attendance")
# @teacher_required
# def class_attendance():
#     tid=session.get('teacher_id')
#     today=datetime.datetime.now().strftime('%A')
    
#     full_schedule=TeacherModel.get_full_schedule(tid)
#     today_list=[row for row in full_schedule if row['day_of_week']==today]
    
#     return render_template('class_attendance.html', 
#                            full_schedule=full_schedule, 
#                            today_schedule=today_list, 
#                            today_name=today)

@teacher_router.get('/class_attendance',response_class=HTMLResponse)
def class_attendance(request:Request):
    teacher_id=request.session.get('teacher_id')
    if not teacher_id:
        return templates.TemplateResponse(request=request,name="teacher_login.html",
                                          context={"error":"Login Again"})
    
    today=datetime.now().strftime('%A')
    from main import app
    try:
        with app.app_context():
            full_schedule=TeacherModel.get_full_schedule(teacher_id)
            if not full_schedule:
                return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                                  context={"error":"No record found"})
            
            today_list=[row for row in full_schedule if row['day_of_week']==today]
            return templates.TemplateResponse(request=request,name="class_attendance.html",
                                              context={"full_schedule":full_schedule,"today_schedule":today_list,
                                                       "today_name":today})
    except Exception as e :
        print(f"Error on class attendance: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                          context={"error":"Try Again"})
    



# @teacher.route("/marked_attendance/<int:section_id>", methods=['GET', 'POST'])
# @teacher_required
# def marked_attendance(section_id):
#     meta=TeacherModel.get_attendance_meta(section_id)
#     if not meta: 
#         return "Error: Schedule not found."

#     cur_date=request.form.get('attendance_date') or request.args.get('date') or str(datetime.date.today())
#     already_marked=TeacherModel.check_attendance_marked(meta['course_schedule_id'], cur_date)

#     if request.method=='POST':
#         if already_marked: 
#             return "Error: Attendance already marked for this date."
            
#         students=TeacherModel.get_student_list_for_attendance(section_id, meta['course_id'])
        
#         batch_data=[
#             (
#                 s['student_course_id'], 
#                 meta['course_schedule_id'], 
#                 cur_date, 
#                 request.form.get(f"status_{s['student_course_id']}", "Absent"), 
#                 s['student_id']
#             ) for s in students
#         ]
        
#         TeacherModel.save_bulk_attendance(batch_data)
#         TeacherModel.save_course_attendance_log(
#             teacher_id=session.get('teacher_id'),
#             course_id=meta['course_id'],
#             course_schedule_id=meta['course_schedule_id'],
#             attendance_date=cur_date,
#             semester=meta['semester'],
#             attendance_data=batch_data
#         )
#         return redirect(url_for('teacher.class_attendance'))

#     student_list=TeacherModel.get_student_list_for_attendance(section_id,meta['course_id'])
#     return render_template('marked_attendance.html', 
#                            course_name=meta['course_name'], 
#                            students=student_list, 
#                            attendance_date=cur_date, 
#                            already_marked=already_marked, 
#                            section_id=section_id)

@teacher_router.get('/marked_attendance/{section_id}',response_class=HTMLResponse)
@teacher_router.post('/marked_attendance/{section_id}',response_class=HTMLResponse)
async def marked_attendance(request:Request,section_id:int,attendance_date:date=Form(None),status_record:Dict=Form(None)):
    teacher_id=request.session.get('teacher_id')
    if not teacher_id:
        return templates.TemplateResponse(request=request,name="teacher_login.html",
        context={"error":"Login Again"})

    flash_success=request.session.pop('flash_success',None)
    flash_error=request.session.pop('flash_error',None)
    from main import app
    try:
        with app.app_context():
            meta=TeacherModel.get_attendance_meta(section_id)
            if not meta:
                return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                                  context={"error":"No record found"})

            course_schedule_id=meta['course_schedule_id']
            course_id=meta['course_id']
            semester=meta['semester']
            course_name=meta['course_name']
            
            query_date=request.query_params.get('date')
            cur_date=attendance_date or (datetime.strptime(query_date,'%Y-%m-%d').date() if query_date else date.today())
            already_marked=TeacherModel.check_attendance_marked(course_schedule_id,cur_date)
            

            if request.method=='POST':
                if already_marked:
                                request.session['flash_error']="Attendance Already Marked"
                                return RedirectResponse(url=f'/marked_attendance/{section_id}?date={cur_date}',status_code=status.HTTP_303_SEE_OTHER)

                form_data=await request.form()
                students=TeacherModel.get_student_list_for_attendance(section_id,course_id)
                batch_data=[
                    (s['student_course_id'],meta['course_schedule_id'],
                     str(cur_date),form_data.get(f"status_{s['student_course_id']}","Absent"),
                    s['student_id']
                    ) for s in students
                ]
                TeacherModel.save_bulk_attendance(batch_data)
                TeacherModel.save_course_attendance_log(teacher_id=teacher_id,course_id=course_id,course_schedule_id=course_schedule_id
                                                        ,semester=semester,attendance_date=str(cur_date),attendance_data=batch_data)
                request.session['flash_success']="Attendance marked successfully"
                return RedirectResponse(url=f'/marked_attendance/{section_id}?date={cur_date}',status_code=status.HTTP_303_SEE_OTHER)


            student_list=TeacherModel.get_student_list_for_attendance(section_id,course_id)
            lec_dict=TeacherModel.get_lecture_no(course_schedule_id)
            lec_no=(lec_dict['total_lectures'] or 0)+1 if isinstance(lec_dict,dict) else 1
            return templates.TemplateResponse(request=request,name="marked_attendance.html",
            context={"course_name":course_name,"students":student_list,"already_marked":already_marked,"section_id":section_id,
                     "attendance_date":cur_date,"lecture_no":lec_no,
                    "flash_error":flash_error,"flash_success":flash_success})

    except Exception as e:
        print(f"Error during marked attendance: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                                          context={"error":"Try Again"})       




# @teacher.route("/class_structure/<int:section_id>")
# @teacher_required
# def class_structure(section_id):
#     info=TeacherModel.get_class_structure(section_id)
#     return render_template('class_structure.html',class_info=info)

@teacher_router.get('/class_structure/{section_id}',response_class=HTMLResponse)
def class_structure(request:Request,section_id:int):
    if request.session.get('role') != 'teacher':
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_401_UNAUTHORIZED)
    
    flash_success=request.session.pop('flash_success',None)
    flash_error=request.session.pop('flash_error',None)
    from main import app
    try:
        with app.app_context():
            info=TeacherModel.get_class_structure(section_id)
            if not info:
                return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
                context={"error":"Try Again"})
            
            return templates.TemplateResponse(request=request,name="class_structure.html",
            context={"class_info":info,"flash_success":flash_success,"flash_error":flash_error})
    except Exception as e:
        print(f"Error during class structure: {str(e)}")
        return templates.TemplateResponse(request=request,name="teacher_dashboard.html",
        context={"error":"Try again"})


# @teacher.route("/generate_result/<int:section_id>",methods=['GET', 'POST'])
# @teacher_required
# def generate_result(section_id):
#     if session.get('role') != 'teacher':
#         return redirect(url_for('main_view'))
    
#     teacher_id=session.get('teacher_id')
#     if not TeacherModel.is_section_owned_by_teacher(section_id, teacher_id):
#         flash('Unauthorized. This section does not belong to you.', 'danger')
#         return redirect(url_for('teacher.teacher_dashboard'))
#     details=TeacherModel.get_attendance_meta(section_id) 
    
#     if request.method=='POST':
#         students=TeacherModel.get_student_list_for_attendance(section_id, details['course_id'])
        
#         for stud in students:
#             sid=stud['student_id']
#             if request.form.get(f'sessional_{sid}'):
#                 s=int(request.form.get(f'sessional_{sid}', 0))
#                 m=int(request.form.get(f'mids_{sid}', 0))
#                 f=int(request.form.get(f'final_{sid}', 0))
#                 total = s + m + f
                
#                 if total >= 80: 
#                     g='A'
#                     gpa=4.0
#                 elif total >= 70: 
#                     g='B'
#                     gpa=3.0 
#                 elif total >= 60: 
#                     g='C'
#                     gpa=2.0
#                 elif total >= 50: 
#                     g='D'
#                     gpa=1.0
#                 else:
#                     g='F'
#                     gpa=0.0           
                
#                 result_data={
#                     'sessional':s, 
#                     'mids':m, 
#                     'final':f, 
#                     'total':total, 
#                     'grade':g, 
#                     'gpa':gpa, 
#                     'status':'Pass' if total >= 50 else 'Fail'
#                 }
                
#                 TeacherModel.process_student_result(sid,section_id,details['course_id'],details['semester'],result_data)
        
#         flash("Results updated successfully!", "success")
#         return redirect(url_for('teacher.teacher_dashboard'))

#     grading_list=TeacherModel.get_grading_data(details['course_id'],section_id)
#     return render_template('generate_result.html',students=grading_list,info=details)

@teacher_router.get("/generate_result/{section_id}",response_class=HTMLResponse)
def generate_result_get(request:Request,section_id:int):
    teacher_id=request.session.get('teacher_id')
    if not teacher_id:
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_401_UNAUTHORIZED)

    from main import app
    try:
        with app.app_context():
            is_owned=TeacherModel.is_section_owned_by_teacher(section_id,teacher_id)
            if not is_owned:
                request.session['flash_error']="Unauthorized Access"
                return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_401_UNAUTHORIZED)

            details=TeacherModel.get_attendance_meta(section_id)
            grading_list=TeacherModel.get_grading_data(details['course_id'],section_id)
            return templates.TemplateResponse(request=request,name="generate_result.html",
                                              context={"students":grading_list,"info":details})
    except Exception as e:
        print(f"Error during generate result page: {str(e)}")


@teacher_router.post("/generate_result/{section_id}")
async def generate_result_post(request:Request,section_id:int):
    teacher_id=request.session.get('teacher_id')
    if not teacher_id:
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_401_UNAUTHORIZED)

    form_data=await request.form()
    from main import app
    try:
        with app.app_context():
            is_owned=TeacherModel.is_section_owned_by_teacher(section_id,teacher_id)
            if not is_owned:
                request.session['flash_error']="Unauthorized Access"
                return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_401_UNAUTHORIZED)

            details=TeacherModel.get_attendance_meta(section_id)
            students=TeacherModel.get_student_list_for_attendance(section_id,details['course_id'])
            for stud in students:
                student_id=stud['student_id']
                sessional_val=form_data.get(f'sessional_{student_id}')
                if sessional_val is not None and sessional_val != '':
                    s=int(sessional_val or 0)
                    m=int(form_data.get(f'mids_{student_id}',0))
                    f_marks=int(form_data.get(f'final_{student_id}',0))
                    total=s+m+f_marks
                    if total>=80:
                        g,gpa= 'A' ,4.0
                    elif total>=70:
                        g,gpa='B',3.0
                    elif total>=60:
                        g,gpa='C',2.0
                    elif total>=50:
                        g,gpa='D',1.0
                    else:
                        g,gpa='F',0.0

                    result_data={
                        'sessional':s,
                        'mids':m,
                        'final':f_marks,
                        'total':total,
                        'grade':g,
                        'gpa':gpa,
                        'status':'Pass' if total >=50 else 'Fail'
                    }   
                    TeacherModel.process_student_result(student_id,section_id,details['course_id'],details['semester'],result_data)

            request.session['flash_success']="Result Updated successfully"
            return RedirectResponse(url=f'/generate_result/{section_id}',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error during posting result: {str(e)}")
        request.session['flash_error']="Failed to updated"
        return RedirectResponse(url=f'/generate_result/{section_id}',status_code=status.HTTP_400_BAD_REQUEST)

                        

# @teacher.route('/fyp_management')
# @teacher_required
# def fyp_management():
#     tid=session.get('teacher_id')
#     groups=TeacherModel.get_fyp_groups(tid)
    
    
#     for g in groups:
#         if g['messages'] and g['messages'][-1]['sender_role']=='student':
#             g['has_unread']=True
#         else:
#             g['has_unread']=False
    
#     stats={
#         'total': len(groups), 
#         'completed': len([g for g in groups if g['status']=='Approved']), 
#         'pending': len([g for g in groups if g['status']=='Pending Approval'])
#     }
    
#     return render_template('fyp_management.html',fyp_data=groups, **stats)


@teacher_router.get('/fyp_management',response_class=HTMLResponse)
def fyp_management(request:Request):
    teacher_id=request.session.get('teacher_id')
    if  not teacher_id:
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_401_UNAUTHORIZED)

    flash_success=request.session.pop('flash_success',None)
    flash_error=request.session.pop('flash_error',None)
    from main import app
    try:
        with app.app_context():
            groups=TeacherModel.get_fyp_groups(teacher_id) or []
            for g in groups:
                if g.get('messages') and g['messages'][-1].get('sender_role')=='student':
                    g['has_unread']=True
                else:
                    g['has_unread']=False

            stats={
                'total':len(groups),
                'completed':len([g for g in groups if g.get('status')=='Approved']),
                'pending':len([g for g in groups if g.get('status')=='Pending Approval'])
            }
            return templates.TemplateResponse(request=request,name="fyp_management.html",
                context={"fyp_data":groups,**stats,"flash_success":flash_success,"flash_error":flash_error})
    except Exception as e:
        print(f"Error loading FYP management: {str(e)}")
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)



# @teacher.route('/approve_fyp/<int:fyp_id>/<string:status>')
# @teacher_required
# def approve_fyp(fyp_id, status):
#     TeacherModel.update_fyp_status(fyp_id, status)
#     flash(f'FYP {status} successfully.', 'success')
#     return redirect(url_for('teacher.fyp_management'))


@teacher_router.get('/approve_fyp/{fyp_id}/{status_val}')
def approve_fyp(request:Request,fyp_id:int,status_val:str):
    if request.session.get('role') != 'teacher':
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)

    try:
        path_data=ApproveFyp(fyp_id=fyp_id,status=status_val)
    except ValidationError:
        request.session['flash_error']="Invalid parameters for FYP approval."
        return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)

    from main import app
    try:
        with app.app_context():
            TeacherModel.update_fyp_status(path_data.fyp_id,path_data.status)
            request.session['flash_success']=f'FYP {path_data.status} successfully.'
            return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error approving FYP: {str(e)}")
        return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)




# @teacher.route('/send_message/<int:fyp_id>', methods=['POST'])
# @teacher_required
# def send_message(fyp_id):
#     if session.get('role') != 'teacher': 
#         return redirect(url_for('main_view'))
        
#     msg_text = request.form.get('message')
#     TeacherModel.add_fyp_message(fyp_id, session.get('teacher_id'), msg_text)
#     return redirect(url_for('teacher.fyp_management'))

@teacher_router.post('/send_message/{fyp_id}')
def send_message(request:Request,fyp_id:int,message:str=Form(...)):
    teacher_id=request.session.get('teacher_id')
    if  not teacher_id:
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        path_data=SendMessagePath(fyp_id=fyp_id)
        form_data=SendMessageForm(message=message)
    except ValidationError:
        request.session['flash_error']="Message cannot be empty."
        return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)

    from main import app
    try:
        with app.app_context():
            TeacherModel.add_fyp_message(path_data.fyp_id,teacher_id,form_data.message)
            return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return RedirectResponse(url='/fyp_management',status_code=status.HTTP_303_SEE_OTHER)



# @teacher.route("/view_submissions/<int:section_id>/<string:sub_type>")
# @login_required
# def view_submissions(section_id,sub_type):
#     if session.get('role') != 'teacher':
#         return redirect(url_for('main_view'))

#     teacher_id=session.get('teacher_id')
#     if not TeacherModel.is_section_owned_by_teacher(section_id, teacher_id):
#         flash('Unauthorized. This section does not belong to you.', 'danger')
#         return redirect(url_for('teacher.teacher_dashboard'))

#     subs, meta=TeacherModel.get_submissions_by_type(section_id,sub_type)
#     title=f"{meta['course_name']} ({meta['section_name']})" if meta else "Submissions"
#     return render_template('view_submissions.html',
#                            submissions=subs,
#                            sub_type=sub_type,
#                            course_name=title,
#                            section_id=section_id)

@teacher_router.get("/view_submissions/{section_id}/{sub_type}",response_class=HTMLResponse)
def view_submissions(request:Request,section_id:int,sub_type:str):
    teacher_id=request.session.get('teacher_id')
    if  not teacher_id:
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)

    try:
        path_data=ViewSubmissionPath(section_id=section_id,sub_type=sub_type)
    except ValidationError:
        request.session['flash_error']="Invalid request parameters."
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)

    from main import app
    try:
        with app.app_context():
            if not TeacherModel.is_section_owned_by_teacher(path_data.section_id,teacher_id):
                request.session['flash_error']='Unauthorized Access'
                return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_401_UNAUTHORIZED)

            subs,meta=TeacherModel.get_submissions_by_type(path_data.section_id,path_data.sub_type)
            title=f"{meta['course_name']} ({meta['section_name']})" if meta else "Submissions"

            return templates.TemplateResponse(request=request,name="view_submissions.html",
                context={"submissions":subs,"sub_type":path_data.sub_type,"course_name":title,"section_id":path_data.section_id})
        
    except Exception as e:
        print(f"Error viewing submissions: {str(e)}")
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)





# @teacher.route("/mark_submission/<int:submission_id>", methods=['POST'])
# @teacher_required
# def mark_submission(submission_id):
#     marks=request.form.get('marks')
#     total=request.form.get('total_marks')
    
#     TeacherModel.update_submission_marks(submission_id, marks, total)
    
#     return redirect(url_for('teacher.view_submissions', 
#                             section_id=request.form.get('section_id'), 
#                             sub_type=request.form.get('sub_type')))

@teacher_router.post("/mark_submission/{submission_id}")
def mark_submission(request:Request,submission_id:int,marks:float=Form(...),total_marks:float=Form(...),
    section_id:int=Form(...),sub_type:str=Form(...)):
    if request.session.get('role') != 'teacher':
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)

    try:
        path_data=MarkSubmissionPath(submission_id=submission_id)
        form_data=MarkSubmissionForm(marks=marks,total_marks=total_marks,section_id=section_id,sub_type=sub_type)
    except ValidationError as e:
        print(f"Mark submission validation error: {e}")
        request.session['flash_error']="Invalid marks values provided."
        return RedirectResponse(url=f'/view_submissions/{section_id}/{sub_type}',status_code=status.HTTP_303_SEE_OTHER)

    from main import app
    try:
        with app.app_context():
            TeacherModel.update_submission_marks(path_data.submission_id,form_data.marks,form_data.total_marks)
            request.session['flash_success']="Marks updated successfully."
            return RedirectResponse(url=f'/view_submissions/{form_data.section_id}/{form_data.sub_type}',status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        print(f"Error marking submission: {str(e)}")
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)



# @teacher.route("/toggle_upload/<int:section_id>/<string:upload_type>",methods=['POST'])
# @login_required
# def toggle_upload(section_id, upload_type):
#     if session.get('role') != 'teacher':
#         return redirect(url_for('main_view'))

#     teacher_id=session.get('teacher_id')
#     if not TeacherModel.is_section_owned_by_teacher(section_id, teacher_id):
#         flash('Unauthorized. This section does not belong to you.', 'danger')
#         return redirect(url_for('teacher.teacher_dashboard'))

#     TeacherModel.toggle_upload_status(section_id, upload_type)
#     flash(f"{upload_type.capitalize()} status updated.", 'success')
#     return redirect(url_for('teacher.teacher_dashboard'))

@teacher_router.post("/toggle_upload/{section_id}/{upload_type}")
def toggle_upload(request:Request,section_id:int,upload_type:str):
    teacher_id=request.session.get('teacher_id')
    if  not teacher_id:
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        path_data=ToggleUploadPath(section_id=section_id,upload_type=upload_type)
    except ValidationError:
        request.session['flash_error']="Invalid upload toggle parameters."
        return RedirectResponse(url=f'/class_structure/{section_id}',status_code=status.HTTP_303_SEE_OTHER)

    from main import app
    try:
        with app.app_context():
            if not TeacherModel.is_section_owned_by_teacher(path_data.section_id,teacher_id):
                request.session['flash_error']='Unauthorized Access'
                return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_401_UNAUTHORIZED)

            TeacherModel.toggle_upload_status(path_data.section_id,path_data.upload_type)
            request.session['flash_success']=f"{path_data.upload_type.capitalize()} status updated."
            return RedirectResponse(url=f'/class_structure/{path_data.section_id}',status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        print(f"Error toggling upload: {str(e)}")
        return RedirectResponse(url=f'/class_structure/{section_id}',status_code=status.HTTP_303_SEE_OTHER)



# @teacher.route('/complaint_suggestion', methods=['GET', 'POST'])
# @teacher_required
# def complaint_suggestion():
#     if request.method=='POST':
#         title=request.form['title']
#         description=request.form['description']
#         user_id=session['user_id']
#         TeacherModel.insert_complaint_suggestion(title, description, user_id)
#         return redirect(url_for('teacher.teacher_dashboard'))
#     return render_template('complaint_suggestion.html')    



@teacher_router.get('/teacher_complaint_suggestion',response_class=HTMLResponse)
@teacher_router.post('/teacher_complaint_suggestion',response_class=HTMLResponse)
def complaint_suggestion(request:Request,title:str=Form(None),description:str=Form(None)):
    user_id=request.session.get('user_id')
    if request.session.get('role') != 'teacher' or not user_id:
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_401_UNAUTHORIZED)

    if request.method=='GET':
        flash_success=request.session.pop('flash_success',None)
        flash_error=request.session.pop('flash_error',None)
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html",
                                          context={"flash_success":flash_success,"flash_error":flash_error})

    try:
        check_data=ComplaintSuggestionForm(title=title,description=description)
    except ValidationError:
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html",
                                          context={"flash_error":"Kindly fill the requirements"})

    from main import app
    try:
        with app.app_context():
            TeacherModel.insert_complaint_suggestion(check_data.title,check_data.description,user_id)
            request.session['flash_success']="Complaint/Suggestion submitted successfully."
            return RedirectResponse(url='/teacher_complaint_suggestion',status_code=status.HTTP_303_SEE_OTHER)
        
    except Exception as e:
        print(f"Error submitting complaint: {str(e)}")
        return templates.TemplateResponse(request=request,name="complaint_suggestion.html",context={"flash_error":"Try Again"})


# @teacher.route('/set_submission_status/<int:submission_id>/<string:status>',methods=['POST'])
# @login_required
# def set_submission_status(submission_id,status):
#     cursor=mysql.connection.cursor()
#     section_id=request.form.get('section_id')
#     sub_type =request.form.get('sub_type')
#     cursor.execute('UPDATE student_submissions SET submission_status=%s WHERE submission_id=%s',
#                    (status, submission_id))
#     mysql.connection.commit()
    
#     flash(f'Status set to {status}.', 'success')
#     return redirect(url_for('teacher.view_submissions',section_id=section_id,sub_type=sub_type))


@teacher_router.post('/set_submission_status/{submission_id}/{status_val}')
def set_submission_status(request:Request,submission_id:int,status_val:str,section_id:int=Form(...),sub_type:str=Form(...)):
    if request.session.get('role') != 'teacher':
        return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)

    try:
        path_data=SetSubmissionStatusPath(submission_id=submission_id,status=status_val)
        form_data=SetSubmissionStatusForm(section_id=section_id,sub_type=sub_type)
    except ValidationError:
        request.session['flash_error']="Invalid parameters for submission status."
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)

    from main import app
    try:
        with app.app_context():
            cursor=mysql.connection.cursor()
            cursor.execute('UPDATE student_submissions SET submission_status=%s WHERE submission_id=%s',(path_data.status,path_data.submission_id))
            mysql.connection.commit()
            cursor.close()

            request.session['flash_success']=f'Status updated to {path_data.status}.'
            return RedirectResponse(url=f'/view_submissions/{form_data.section_id}/{form_data.sub_type}',status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        print(f"Error updating submission status: {str(e)}")
        return RedirectResponse(url='/teacher_dashboard',status_code=status.HTTP_303_SEE_OTHER)