from functools import wraps
from flask import session, redirect, url_for,request
import MySQLdb.cursors
from utils.db import mysql
from fastapi import Depends,HTTPException,Request
from typing import Optional



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main_view'))

        if session.get('role')=='student':
            cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT student_id FROM students WHERE user_id=%s AND is_deleted=0',
                (session['user_id'],)
            )
            student=cursor.fetchone()
            cursor.close()
            if not student:
                session.clear()  
                return redirect(url_for('main_view'))
            
        elif session.get('role')=='teacher':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT teacher_id FROM teachers WHERE user_id=%s AND is_deleted=0',
                (session['user_id'],)
            )
            teacher=cursor.fetchone()
            cursor.close()
            if not teacher:
                session.clear()
                return redirect(url_for('main_view'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in request.session:
            return redirect(url_for('main_view'))
        if session.get('role') != 'student':
            return redirect(url_for('main_view'))
        
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT student_id FROM students WHERE user_id=%s AND is_deleted=0',
            (session['user_id'],)
        )
        if not cursor.fetchone():
            cursor.close()
            session.clear()
            return redirect(url_for('main_view'))
        cursor.close()
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main_view'))
        if session.get('role') != 'teacher':
            return redirect(url_for('main_view'))
        
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT teacher_id FROM teachers WHERE user_id=%s AND is_deleted=0',
            (session['user_id'],)
        )
        if not cursor.fetchone():
            cursor.close()
            session.clear()
            return redirect(url_for('main_view'))
        cursor.close()
        return f(*args, **kwargs)
    return decorated_function   


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main_view'))
        if session.get('role') != 'admin':
            return redirect(url_for('main_view'))
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT admin_id FROM admins WHERE admin_id=%s',
            (session.get('admin_id'),)
        )
        if not cursor.fetchone():
            cursor.close()
            session.clear()
            return redirect(url_for('main_view'))
        cursor.close()
        return f(*args, **kwargs)
    return decorated_function
