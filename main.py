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
from students_module.students_routes import router as student_router
from teachers_module.teachers_routes import router as teacher_router


app=FastAPI()
app.add_middleware(SessionMiddleware,secret_key=SECRET_KEY,max_age=3600)
app.mount("/static",StaticFiles(directory=os.path.join(BASE_DIR,"static")),name="static")
templates=Jinja2Templates(directory=os.path.join(BASE_DIR,'templates'))

app.include_router(student_router)
app.include_router(teacher_router)

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
            error_msg="Please enter valid data"
            return templates.TemplateResponse(request=request,name="user_signup.html",context={"error":error_msg})
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error during signup: {str(e)}")
    return templates.TemplateResponse(request=request,name="user_signup.html",context={"error":error})     



@app.get("/reset_password",response_class=HTMLResponse)
@app.post("/reset_password",response_class=HTMLResponse)
def reset_password(request:Request,email:str=Form(None),new_password:str=Form(None)):
    error=None
    if request.method=='POST':
        user=MainModel.get_user_by_email(email)
        if not user:
            return RedirectResponse(url='/user_signup',status_code=status.HTTP_303_SEE_OTHER)

        MainModel.update_password(email,new_password)
        role=request.session.get('role')
        if role=='student':
            return RedirectResponse(url='/student_login',status_code=status.HTTP_303_SEE_OTHER)
        elif role=='teacher':
            return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)
        elif role=='admin':
            return RedirectResponse(url='/admin_login',status_code=status.HTTP_303_SEE_OTHER)
        else:
            user_data=MainModel.get_user_by_email(email)
            if user_data:
                if user_data['role_id']==2:
                    return RedirectResponse(url='/student_login',status_code=status.HTTP_303_SEE_OTHER)
                elif user_data['role_id']==1:
                    return RedirectResponse(url='/teacher_login',status_code=status.HTTP_303_SEE_OTHER)
                elif user_data['role_id']==3:
                     return RedirectResponse(url='/admin_login',status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request,name="reset_password.html",context={"error":error})         


@app.get("/logout")
def logout(request:Request):
    request.session.clear()
    return RedirectResponse(url='/main_view',status_code=status.HTTP_303_SEE_OTHER)


if __name__=='__main__':
    uvicorn.run("main:app",host="127.0.0.1",port=50001,reload=True)



        














# from flask import Flask,render_template,request,redirect,url_for,session
# from datetime import date,timedelta
# from utils.db import mysql
# from utils.auth import login_required
# from students_module.students_routes import student,router as student_router
# from teachers_module.teachers_routes import teacher,teacher_router as teach_router
# from admin.admin_routes import admin
# from werkzeug.exceptions import RequestEntityTooLarge
# from config import *
# from models import MainModel
# import os
# import re
# import uvicorn
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from starlette.middleware.sessions import SessionMiddleware
# from fastapi.middleware.wsgi import WSGIMiddleware


# app=Flask(__name__,template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates'))
# app.config['FEE_UPLOAD_FOLDER']=FEE_UPLOAD_FOLDER
# app.config['TEMPLATES_AUTO_RELOAD']=TEMPLATES_AUTO_RELOAD
# app.config['MYSQL_HOST']=MYSQL_HOST
# app.config['MYSQL_USER']=MYSQL_USER
# app.config['MYSQL_PASSWORD']=MYSQL_PASSWORD
# app.config['MYSQL_DB']=MYSQL_DB
# app.config['MYSQL_PORT']=3306
# app.config['SECRET_KEY']=SECRET_KEY
# app.config['MYSQL_CURSORCLASS']='DictCursor'
# app.permanent_session_lifetime=timedelta(minutes=7)

# mysql.init_app(app)

# app.register_blueprint(student)
# app.register_blueprint(teacher)
# app.register_blueprint(admin)

# app.config['MAX_CONTENT_LENGTH']=5 * 1024 * 1024
# EMAIL_PATTERN=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


# @app.route('/main_view',methods=['GET','POST'])
# def main_view():
#     if request.method=='POST':
#         if 'student' in request.form:
#             return redirect('/student_login')
#         elif 'teacher' in request.form:
#             return redirect('/teacher_login')
#         elif 'admin' in request.form:
#             return redirect(url_for('admin.admin_login'))

#     return render_template('main_view.html')


# @app.route('/user_signup',methods=['GET','POST'])
# def user_signup():
#     if request.method=='POST':
#         email=request.form['email']
#         if not re.match(EMAIL_PATTERN,email):
#             error="Please enter a valid Gmail address (example@gmail.com)."
#             return render_template('user_signup.html',error=error)

#         password=request.form['password']
#         user_type=request.form.get('user_type')

#         user=MainModel.get_user_by_email(email)
#         if user:
#             if user['role_id'] == 2:
#                 return redirect('/student_login')
#             elif user['role_id'] == 1:
#                 # return redirect(url_for('teacher.teacher_login'))
#                 return redirect('/teacher_login')
#         else:
#             if user_type == 'student':
#                 role_id=2
#             elif user_type == 'teacher':
#                 role_id=1
#             elif user_type == 'admin':
#                 role_id=3
#             else:
#                 role_id=None

#             user_id=MainModel.insert_user(email,password,role_id)
#             if user_type=='student':
#                 MainModel.insert_student(user_id)
#                 return redirect('/student_login')
#             elif user_type=='teacher':
#                 MainModel.insert_teacher(user_id)
#                 # return redirect(url_for('teacher.teacher_login'))
#                 return redirect('/teacher_login')

#     return render_template('user_signup.html',error=None)


# @app.route('/reset_password',methods=['GET','POST'])
# def reset_password():
#     if request.method=='POST':
#         email=request.form['email']
#         new_password=request.form['new_password']

#         user=MainModel.get_email_from_users(email)
#         if not user:
#             return redirect('/user_signup')

#         MainModel.update_password(email,new_password)
#         role=session.get('role')
#         if role=='student':
#             return redirect('/student_login')
#         elif role=='teacher':
#             # return redirect(url_for('teacher.teacher_login'))
#             return redirect('/teacher_login')
#         elif role=='admin':
#             return redirect(url_for('admin.admin_login'))
#         else:
#             user_data=MainModel.get_user_by_email(email)
#             if user_data:
#                 if user_data['role_id']==2:
#                     return redirect('/student_login')
#                 elif user_data['role_id']==1:
#                     # return redirect(url_for('teacher.teacher_login'))
#                     return redirect('/teacher_login')
#                 elif user_data['role_id']==3:
#                     return redirect(url_for('admin.admin_login'))

#     return render_template('reset_password.html')


# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('main_view'))


# fastapi_app=FastAPI()
# fastapi_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
# fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")
# fastapi_app.include_router(student_router)
# fastapi_app.include_router(teach_router)
# fastapi_app.mount("/", WSGIMiddleware(app))

# if __name__ == '__main__':
#     uvicorn.run("main:fastapi_app", host="127.0.0.1", port=50001, reload=True)