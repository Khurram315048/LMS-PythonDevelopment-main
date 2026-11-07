import time
import logging
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Form, status, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import ValidationError
from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request, status
from core.csrf import get_csrf_token, verify_csrf
from core.templating import get_templates
from shared.mail import send_email
from modules.auth.repository import MainModel
from modules.auth.schema import SignupUser

router=APIRouter(dependencies=[Depends(verify_csrf)])
templates=get_templates("auth")
templates.env.globals["csrf_token"]=get_csrf_token



def generate_otp()->str:
    return f"{secrets.randbelow(1_000_000):06d}"


def otp_expiry(minutes:int=10)->datetime:
    return datetime.now() + timedelta(minutes=minutes)

LOGIN_BY_ROLE={2:'/student_login',1:'/teacher_login',3:'/admin_login'}

max_attempt=5


@router.get("/main_view",response_class=HTMLResponse)
@router.post("/main_view",response_class=HTMLResponse)
async def main_view(request:Request):
    error=None
    if request.method=='POST':
        form=await request.form()
        if 'student' in form:
            return RedirectResponse(url='/student_login',status_code=status.HTTP_303_SEE_OTHER)
        elif 'teacher' in form:
            return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)
        elif 'admin' in form:
            return RedirectResponse(url='/admin_login',status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request,name="main_view.html",context={"error":error})


@router.get("/user_signup",response_class=HTMLResponse)
async def user_signup(request:Request):
    error=None
    return templates.TemplateResponse(request=request,name="user_signup.html",context={"error":error})


@router.post("/user_signup",response_class=HTMLResponse)
async def user_signup(request:Request,first_name:str=Form(...),last_name=Form(...),contact:int=Form(...),email:str=Form(...),
                      password:str=Form(...),user_type=Form(...)):
    error=None
    if request.method=='POST':
        try:
            valid_data=SignupUser(
                first_name=first_name,
                last_name=last_name,
                contact=contact,
                email=email,
                password=password,
                user_type=user_type
            )

            user=MainModel.get_user_by_email(valid_data.email)
            if user:
                if user['role_id']==2:
                    return RedirectResponse(url='/student_login',status_code=status.HTTP_303_SEE_OTHER)
                elif user['role_id']==1:
                    return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)
            else:
                role_id=2 if valid_data.user_type=='student' else (1 if valid_data.user_type=='teacher' else 3)
                user_id=MainModel.insert_user(valid_data.email,valid_data.password,role_id)
                if valid_data.user_type=='student':
                    MainModel.insert_student(user_id,valid_data.first_name,valid_data.last_name,valid_data.contact,valid_data.email)
                    return RedirectResponse(url='/student_login',status_code=status.HTTP_303_SEE_OTHER)
                elif valid_data.user_type=='teacher':
                    MainModel.insert_teacher(user_id,valid_data.first_name,valid_data.last_name,valid_data.contact,valid_data.email)

                    return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)

        except ValidationError as v:
            logging.warning(f"Main sinup route validation: {str(v)}")
            error_msg="Please enter valid data"
            return templates.TemplateResponse(request=request,name="user_signup.html",context={"error":error_msg})

        except Exception as e:
            logging.exception(f"signup route main api: {str(e)}")
    return templates.TemplateResponse(request=request,name="user_signup.html",context={"error":error})


@router.get('/send_reset_email',response_class=HTMLResponse)
@router.post('/send_reset_email',response_class=HTMLResponse)
def send_reset_email(request:Request,background_tasks:BackgroundTasks,email:str=Form(None)):
    if request.method=='GET':
        return templates.TemplateResponse(request=request,name="send_reset_email.html")
    try:
        email=(email or '').strip()
        user=MainModel.get_user_by_email(email)
        if not user:
            request.session['flash_error']="Kindly register"
            return RedirectResponse(url='/user_signup',status_code=status.HTTP_303_SEE_OTHER)
        else:
            otp=generate_otp()
            MainModel.insert_otp(user['user_id'],otp,otp_expiry(10))
            background_tasks.add_task(send_email,[email],"Password Reset Code",otp)
        request.session['reset_email']=email
        request.session['flash_success']="Code has been sent on registered email"
        return RedirectResponse(url='/otp_verify',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"during snd rst email(main): {str(e)}")
        return templates.TemplateResponse(request=request,name="send_reset_email.html",
                                          context={"error":"Try again"})


@router.get('/otp_verify',response_class=HTMLResponse)
@router.post('/otp_verify',response_class=HTMLResponse)
def otp_verify(request:Request,otp:str=Form(None)):
    email=request.session.get('reset_email')
    if not email:
        return RedirectResponse(url='/send_reset_email',status_code=status.HTTP_303_SEE_OTHER)

    if request.method=='GET':
        return templates.TemplateResponse(request=request,name="otp_verify.html",
                                          context={"flash_success":request.session.pop('flash_success',None)})
    try:
        generic="Invalid or expired code"
        user=MainModel.get_user_by_email(email)
        row=MainModel.get_otp(user['user_id']) if user else None

        if (not row or row['otp_used'] or row['otp_expire']<datetime.now()
                or (row['otp_attempts'] or 0)>=max_attempt):
            return templates.TemplateResponse(request=request,name="otp_verify.html",context={"error":generic})

        if str(row['otp_num']).zfill(6)!=(otp or '').strip():
            MainModel.increment_otp_attempts(row['otp_id'])
            return templates.TemplateResponse(request=request,name="otp_verify.html",context={"error":generic})

        request.session.pop('reset_email',None)
        request.session['verified_email']=email
        request.session['verified_role_id']=user['role_id']
        request.session['verified_at']=int(time.time())
        MainModel.mark_otp_used(row['otp_id'])
        return RedirectResponse(url='/update_password',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"during otp verify(main): {str(e)}")
        return templates.TemplateResponse(request=request,name="otp_verify.html",context={"error":"Try again"})


@router.get('/update_password',response_class=HTMLResponse)
@router.post('/update_password',response_class=HTMLResponse)
def update_password(request:Request,new_password:str=Form(None),confirm_password:str=Form(None)):
    email=request.session.get('verified_email')
    if not email or time.time()-request.session.get('verified_at',0)>600:
        for k in ('verified_email','verified_role_id','verified_at'):
            request.session.pop(k,None)
        return RedirectResponse(url='/send_reset_email',status_code=status.HTTP_303_SEE_OTHER)

    if request.method=='GET':
        return templates.TemplateResponse(request=request,name="update_password.html")
    try:
        if not new_password or len(new_password)<8:
            return templates.TemplateResponse(request=request,name="update_password.html",
                                              context={"error":"Min 8 characters"})
        if new_password!=confirm_password:
            return templates.TemplateResponse(request=request,name="update_password.html",
                                              context={"error":"Passwords do not match"})

        MainModel.update_password(email,new_password)
        role_id=request.session.get('verified_role_id')
        for k in ('verified_email','verified_role_id','verified_at'):
            request.session.pop(k,None)
        return RedirectResponse(url=LOGIN_BY_ROLE.get(role_id,'/main_view'),status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"during update password(main): {str(e)}")
        return templates.TemplateResponse(request=request,name="update_password.html",context={"error":"Try again"})


@router.post("/logout")
def logout(request:Request):
    request.session.clear()
    response=RedirectResponse(url="/main_view",status_code=status.HTTP_303_SEE_OTHER,)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response