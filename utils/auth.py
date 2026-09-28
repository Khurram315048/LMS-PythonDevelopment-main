# from functools import wraps
# from flask import session, redirect, url_for,request
# import MySQLdb.cursors
# from utils.db import mysql
# from fastapi import Depends,HTTPException,Request
# from typing import Optional



# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('main_view'))

#         if session.get('role')=='student':
#             cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             cursor.execute(
#                 'SELECT student_id FROM students WHERE user_id=%s AND is_deleted=0',
#                 (session['user_id'],)
#             )
#             student=cursor.fetchone()
#             cursor.close()
#             if not student:
#                 session.clear()  
#                 return redirect(url_for('main_view'))
            
#         elif session.get('role')=='teacher':
#             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             cursor.execute(
#                 'SELECT teacher_id FROM teachers WHERE user_id=%s AND is_deleted=0',
#                 (session['user_id'],)
#             )
#             teacher=cursor.fetchone()
#             cursor.close()
#             if not teacher:
#                 session.clear()
#                 return redirect(url_for('main_view'))
#         return f(*args, **kwargs)
#     return decorated_function


# def student_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in request.session:
#             return redirect(url_for('main_view'))
#         if session.get('role') != 'student':
#             return redirect(url_for('main_view'))
        
#         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute(
#             'SELECT student_id FROM students WHERE user_id=%s AND is_deleted=0',
#             (session['user_id'],)
#         )
#         if not cursor.fetchone():
#             cursor.close()
#             session.clear()
#             return redirect(url_for('main_view'))
#         cursor.close()
#         return f(*args, **kwargs)
#     return decorated_function


# def teacher_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('main_view'))
#         if session.get('role') != 'teacher':
#             return redirect(url_for('main_view'))
        
#         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute(
#             'SELECT teacher_id FROM teachers WHERE user_id=%s AND is_deleted=0',
#             (session['user_id'],)
#         )
#         if not cursor.fetchone():
#             cursor.close()
#             session.clear()
#             return redirect(url_for('main_view'))
#         cursor.close()
#         return f(*args, **kwargs)
#     return decorated_function   


# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('main_view'))
#         if session.get('role') != 'admin':
#             return redirect(url_for('main_view'))
#         cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute(
#             'SELECT admin_id FROM admins WHERE admin_id=%s',
#             (session.get('admin_id'),)
#         )
#         if not cursor.fetchone():
#             cursor.close()
#             session.clear()
#             return redirect(url_for('main_view'))
#         cursor.close()
#         return f(*args, **kwargs)
#     return decorated_function





from fastapi import Request,HTTPException,status


def get_current_user(request:Request)->dict:
    user_id=request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                            headers={"location": "/main_view"})

    return {"user_id":user_id}


def get_current_student(request:Request)->dict:
    student_id=request.session.get('student_id')
    user_id=request.session.get('user_id')
    role=request.session.get('role')
    
    if role != 'student' or not student_id or not user_id:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                                    headers={"location": "/student_login"})

    return {"student_id":student_id,"user_id":user_id,"role":role}


def get_current_teacher(request:Request)->dict:
    teacher_id=request.session.get('teacher_id')
    user_id=request.session.get('user_id')
    role=request.session.get('role')
    
    if role != 'teacher' or not teacher_id or not user_id:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                                    headers={"location": "/teacher_login"})

    return {"teacher_id":teacher_id,"user_id":user_id,"role":role}



def get_current_admin(request:Request)->dict:
    admin_id=request.session.get('admin_id')
    user_id=request.session.get('user_id')
    role=request.session.get('role')
    
    if role != 'admin' or not admin_id or not user_id:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                                    headers={"location": "/admin_login"})

    return {"admin_id":admin_id,"user_id":user_id,"role":role}  
