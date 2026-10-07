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



        











