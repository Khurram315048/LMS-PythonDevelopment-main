import os
import re
import uvicorn
from fastapi import FastAPI,Request,Form,status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel ,EmailStr,Field,ValidationError
from config import SECRET_KEY,BASE_DIR
from models import MainModel
import utils.logger
import logging
from fastapi import BackgroundTasks
import time
from datetime import datetime,timedelta
from utils.send_mail import send_email
from routes.websocket_routes import router as websocket_router
from students_module.students_routes import router as student_router
from teachers_module.teachers_routes import router as teacher_router
from admin.admin_routes import router as admin_router
import secrets

def generate_otp()->str:
    return f"{secrets.randbelow(1_000_000):06d}"


def otp_expiry(minutes:int=10)->datetime:
    return datetime.now() + timedelta(minutes=minutes)

LOGIN_BY_ROLE={2:'/student_login',1:'/teacher_login',3:'/admin_login'}

max_attempt=5

app=FastAPI()
app.add_middleware(SessionMiddleware,secret_key=SECRET_KEY,max_age=3600)
app.mount("/static",StaticFiles(directory=os.path.join(BASE_DIR,"static")),name="static")
templates=Jinja2Templates(directory=os.path.join(BASE_DIR,'templates'))

app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(admin_router)
app.include_router(websocket_router)

EMAIL_PATTERN=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]\.[a-zA-Z]{2,}$'

class SignupUser(BaseModel):
    first_name:str=Field(...,min_length=2)
    last_name:str=Field(...,min_length=2)
    contact:int
    email:EmailStr
    password:str=Field(...,min_length=8)
    user_type:str=Field(...,pattern="^(student|teacher|admin)$")



@app.get("/main_view",response_class=HTMLResponse)
@app.post("/main_view",response_class=HTMLResponse)
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


@app.get("/user_signup",response_class=HTMLResponse)
async def user_signup(request:Request):
    error=None
    return templates.TemplateResponse(request=request,name="user_signup.html",context={"error":error})


@app.post("/user_signup",response_class=HTMLResponse)
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




    
    



# @app.get("/reset_password",response_class=HTMLResponse)
# @app.post("/reset_password",response_class=HTMLResponse)
# def reset_password(request:Request,email:str=Form(None),new_password:str=Form(None)):
#     error=None
#     if request.method=='POST':
#         user=MainModel.get_user_by_email(email)
#         if not user:
#             logging.error(f"rst psswrd route api")
#             return RedirectResponse(url='/user_signup',status_code=status.HTTP_303_SEE_OTHER)

#         MainModel.update_password(email,new_password)
#         role=request.session.get('role')
#         if role=='student':
#             return RedirectResponse(url='/student_login',status_code=status.HTTP_303_SEE_OTHER)
#         elif role=='teacher':
#             return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)
#         elif role=='admin':
#             return RedirectResponse(url='/admin_login',status_code=status.HTTP_303_SEE_OTHER)
#         else:
#             user_data=MainModel.get_user_by_email(email)
#             if user_data:
#                 if user_data['role_id']==2:
#                     return RedirectResponse(url='/student_login',status_code=status.HTTP_303_SEE_OTHER)
#                 elif user_data['role_id']==1:
#                     return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)
#                 elif user_data['role_id']==3:
#                      return RedirectResponse(url='/admin_login',status_code=status.HTTP_303_SEE_OTHER)

#     return templates.TemplateResponse(request=request,name="reset_password.html",context={"error":error})         


@app.get('/send_reset_email',response_class=HTMLResponse)
@app.post('/send_reset_email',response_class=HTMLResponse)
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
        request.session['flash_success']="If the email is registered, a code has been sent"
        return RedirectResponse(url='/otp_verify',status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.exception(f"during snd rst email(main): {str(e)}")
        return templates.TemplateResponse(request=request,name="send_reset_email.html",
                                          context={"error":"Try again"})


@app.get('/otp_verify',response_class=HTMLResponse)
@app.post('/otp_verify',response_class=HTMLResponse)
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


@app.get('/update_password',response_class=HTMLResponse)
@app.post('/update_password',response_class=HTMLResponse)
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


@app.get("/logout")
def logout(request:Request):
    request.session.clear()
    response=RedirectResponse(url='/main_view',status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
    # return RedirectResponse(url='/main_view',status_code=status.HTTP_303_SEE_OTHER)


if __name__=='__main__':
    uvicorn.run("main:app",host="127.0.0.1",port=50001,reload=True)



        











